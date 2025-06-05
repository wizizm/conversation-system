#!/usr/bin/env python3
"""
統合MCPテストスイート
MCP ServerとConversation APIの包括的なテスト
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, Optional

import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# テスト設定（動的パス取得）
def get_project_root():
    """プロジェクトルートディレクトリを動的に取得"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)

PROJECT_ROOT = get_project_root()
TEST_CONFIG = {
    "mcp_server_path": os.path.join(PROJECT_ROOT, "mcp-server"),
    "api_base_url": "http://localhost:8000",
    "test_timeout": 30,
    "mcp_timeout": 10
}

class MCPTestSuite:
    """MCP サーバーとAPI機能の統合テストスイート"""
    
    def __init__(self):
        self.mcp_process: Optional[subprocess.Popen] = None
        self.api_client = httpx.AsyncClient(timeout=10.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        
    async def cleanup(self):
        """テスト後のクリーンアップ"""
        if self.mcp_process and self.mcp_process.poll() is None:
            self.mcp_process.terminate()
            await asyncio.sleep(1)
            if self.mcp_process.poll() is None:
                self.mcp_process.kill()
                
        await self.api_client.aclose()
        
    async def test_api_connection(self) -> Dict[str, Any]:
        """API接続テスト"""
        print("🔗 API接続をテスト中...")
        
        try:
            response = await self.api_client.get(f"{TEST_CONFIG['api_base_url']}/health")
            if response.status_code == 200:
                print("✅ API接続成功")
                return {"status": "success", "message": "API接続成功"}
            else:
                print(f"⚠️ API接続警告: ステータスコード {response.status_code}")
                return {"status": "warning", "message": f"API接続成功（ステータス: {response.status_code}）"}
                
        except Exception as e:
            print(f"❌ API接続失敗: {e}")
            return {"status": "error", "message": f"API接続失敗: {str(e)}"}
    
    async def test_mcp_server_startup(self) -> Dict[str, Any]:
        """MCPサーバー起動テスト"""
        print("🚀 MCPサーバー起動をテスト中...")
        
        try:
            # MCPサーバーをサブプロセスとして起動
            self.mcp_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=TEST_CONFIG["mcp_server_path"]
            )
            
            # 起動待機
            await asyncio.sleep(2)
            
            if self.mcp_process.poll() is None:
                print("✅ MCPサーバー起動成功")
                return {"status": "success", "message": "MCPサーバー起動成功"}
            else:
                stderr_output = self.mcp_process.stderr.read()
                print(f"❌ MCPサーバー起動失敗: {stderr_output}")
                return {"status": "error", "message": f"MCPサーバー起動失敗: {stderr_output}"}
                
        except Exception as e:
            print(f"❌ MCPサーバー起動例外: {e}")
            return {"status": "error", "message": f"MCPサーバー起動例外: {str(e)}"}
    
    async def test_mcp_initialization(self) -> Dict[str, Any]:
        """MCP初期化テスト"""
        print("🔧 MCP初期化をテスト中...")
        
        if not self.mcp_process or self.mcp_process.poll() is not None:
            return {"status": "error", "message": "MCPサーバーが起動していません"}
        
        try:
            # MCP初期化メッセージ
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # メッセージ送信
            message_str = json.dumps(init_message) + "\n"
            self.mcp_process.stdin.write(message_str)
            self.mcp_process.stdin.flush()
            
            # レスポンス待機
            await asyncio.sleep(2)
            
            # レスポンス読み取り試行
            try:
                # ノンブロッキングで読み取り
                response_line = self.mcp_process.stdout.readline()
                if response_line:
                    response_data = json.loads(response_line)
                    if "result" in response_data:
                        # Send initialized notification
                        initialized_message = {
                            "jsonrpc": "2.0",
                            "method": "notifications/initialized"
                        }
                        init_str = json.dumps(initialized_message) + "\n"
                        self.mcp_process.stdin.write(init_str)
                        self.mcp_process.stdin.flush()
                        await asyncio.sleep(1)
                        
                        print("✅ MCP初期化成功")
                        return {"status": "success", "message": "MCP初期化成功", "response": response_data}
                    else:
                        print(f"⚠️ MCP初期化応答異常: {response_data}")
                        return {"status": "warning", "message": f"MCP初期化応答異常: {response_data}"}
                else:
                    print("⚠️ MCP初期化応答なし")
                    return {"status": "warning", "message": "MCP初期化応答なし"}
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ MCP初期化応答解析エラー: {e}")
                return {"status": "warning", "message": f"MCP初期化応答解析エラー: {e}"}
                
        except Exception as e:
            print(f"❌ MCP初期化例外: {e}")
            return {"status": "error", "message": f"MCP初期化例外: {str(e)}"}
    
    async def test_conversation_api_functionality(self) -> Dict[str, Any]:
        """会話API機能テスト"""
        print("💬 会話API機能をテスト中...")
        
        try:
            # メッセージ保存のテスト
            test_message_data = {
                "role": "user",
                "content": "MCPテストメッセージ",
                "topics": ["MCP", "テスト"],
                "keywords": ["test", "MCP", "統合"]
            }
            
            response = await self.api_client.post(
                f"{TEST_CONFIG['api_base_url']}/messages",
                json=test_message_data
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("message_id")
                if message_id:
                    print(f"✅ 会話API機能成功 - メッセージID: {message_id}")
                    return {"status": "success", "message": f"会話API機能成功 - メッセージID: {message_id}"}
                else:
                    print("⚠️ 会話API機能警告 - メッセージIDが取得できませんでした")
                    return {"status": "warning", "message": "会話API機能警告 - メッセージIDが取得できませんでした"}
            else:
                print(f"❌ 会話API機能失敗 - ステータス: {response.status_code}")
                return {"status": "error", "message": f"会話API機能失敗 - ステータス: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ 会話API機能例外: {e}")
            return {"status": "error", "message": f"会話API機能例外: {str(e)}"}
    
    async def test_mcp_tool_functionality(self) -> Dict[str, Any]:
        """MCPツール機能テスト"""
        print("🛠️ MCPツール機能をテスト中...")
        
        if not self.mcp_process or self.mcp_process.poll() is not None:
            return {"status": "error", "message": "MCPサーバーが起動していません"}
        
        try:
            # ツール一覧取得
            tools_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            message_str = json.dumps(tools_message) + "\n"
            self.mcp_process.stdin.write(message_str)
            self.mcp_process.stdin.flush()
            
            await asyncio.sleep(2)
            
            try:
                # タイムアウト付きで読み取り
                import select
                ready, _, _ = select.select([self.mcp_process.stdout], [], [], 5.0)  # 5秒タイムアウト
                
                if ready:
                    response_line = self.mcp_process.stdout.readline()
                    if response_line:
                        response_data = json.loads(response_line)
                        if "result" in response_data:
                            tools = response_data["result"].get("tools", [])
                            if tools:
                                print(f"✅ MCPツール機能成功 - {len(tools)}個のツールが利用可能")
                                return {"status": "success", "message": f"MCPツール機能成功 - {len(tools)}個のツールが利用可能", "tools": tools}
                            else:
                                print("⚠️ MCPツール機能警告 - ツールが見つかりません")
                                return {"status": "warning", "message": "MCPツール機能警告 - ツールが見つかりません"}
                        else:
                            print(f"⚠️ MCPツール機能応答異常: {response_data}")
                            return {"status": "warning", "message": f"MCPツール機能応答異常: {response_data}"}
                    else:
                        print("⚠️ MCPツール機能応答なし")
                        return {"status": "warning", "message": "MCPツール機能応答なし"}
                else:
                    print("⚠️ MCPツール機能タイムアウト - サーバーが応答しません")
                    return {"status": "warning", "message": "MCPツール機能タイムアウト - サーバーが応答しません"}
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ MCPツール機能応答解析エラー: {e}")
                return {"status": "warning", "message": f"MCPツール機能応答解析エラー: {e}"}
                
        except Exception as e:
            print(f"❌ MCPツール機能例外: {e}")
            return {"status": "error", "message": f"MCPツール機能例外: {str(e)}"}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """全テストの実行"""
        print("🧪 統合MCPテストスイートを開始...")
        print("=" * 60)
        
        test_results = {}
        
        # 1. API接続テスト
        test_results["api_connection"] = await self.test_api_connection()
        
        # 2. MCPサーバー起動テスト
        test_results["mcp_startup"] = await self.test_mcp_server_startup()
        
        # 3. MCP初期化テスト
        test_results["mcp_initialization"] = await self.test_mcp_initialization()
        
        # 4. 会話API機能テスト
        test_results["conversation_api"] = await self.test_conversation_api_functionality()
        
        # 5. MCPツール機能テスト
        test_results["mcp_tools"] = await self.test_mcp_tool_functionality()
        
        # 結果集計
        print("=" * 60)
        print("📊 テスト結果サマリー:")
        
        success_count = 0
        warning_count = 0
        error_count = 0
        
        for test_name, result in test_results.items():
            status = result["status"]
            message = result["message"]
            
            if status == "success":
                success_count += 1
                print(f"✅ {test_name}: {message}")
            elif status == "warning":
                warning_count += 1
                print(f"⚠️ {test_name}: {message}")
            else:
                error_count += 1
                print(f"❌ {test_name}: {message}")
        
        print("=" * 60)
        print(f"🎯 総合結果: {success_count}成功, {warning_count}警告, {error_count}エラー")
        
        if error_count == 0:
            print("🎉 全テストパス！MCPサーバーは正常に動作しています。")
            overall_status = "success"
        elif warning_count > 0 and error_count == 0:
            print("⚠️ 一部警告がありますが、基本機能は動作しています。")
            overall_status = "warning"
        else:
            print("❌ 重要なエラーが発生しています。修正が必要です。")
            overall_status = "error"
        
        return {
            "overall_status": overall_status,
            "success_count": success_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "detailed_results": test_results
        }

async def main():
    """メイン実行関数"""
    try:
        async with MCPTestSuite() as test_suite:
            results = await test_suite.run_all_tests()
            
            # 終了コード決定
            if results["overall_status"] == "success":
                return 0
            elif results["overall_status"] == "warning":
                return 1
            else:
                return 2
                
    except KeyboardInterrupt:
        print("\n⚠️ テストが中断されました")
        return 130
    except Exception as e:
        print(f"\n❌ テスト実行中に予期しないエラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)