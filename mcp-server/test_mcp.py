#!/usr/bin/env python3
"""
Enhanced 統合MCPテストスイート v2.0
MCP ServerとConversation APIの包括的なテスト（新機能対応）
拡張機能：
- スマート圧縮システム
- 適応的詳細レベル
- 技術用語検索  
- 拡張分析機能
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
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
    "api_base_url": "http://localhost:9000",
    "test_timeout": 30,
    "mcp_timeout": 10
}

class EnhancedMCPTestSuite:
    """Enhanced MCP サーバーとAPI機能の統合テストスイート v2.0"""
    
    def __init__(self):
        self.mcp_process: Optional[subprocess.Popen] = None
        self.api_client = httpx.AsyncClient(timeout=15.0)
        self.test_message_id = None
        
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
        
    async def test_enhanced_api_connection(self) -> Dict[str, Any]:
        """Enhanced API接続テスト（v2.0機能確認）"""
        print("🔗 Enhanced API接続をテスト中...")
        
        try:
            response = await self.api_client.get(f"{TEST_CONFIG['api_base_url']}/health")
            if response.status_code == 200:
                health_data = response.json()
                version = health_data.get('version', 'unknown')
                features = health_data.get('features', [])
                stats = health_data.get('stats', {})
                
                print(f"✅ Enhanced API接続成功 (version: {version})")
                
                # v2.0機能確認
                expected_features = ["smart_compression", "multi_layer_summary", "adaptive_context"]
                missing_features = [f for f in expected_features if f not in features]
                
                if missing_features:
                    print(f"⚠️ 一部v2.0機能が見つかりません: {missing_features}")
                    return {"status": "warning", "message": f"v2.0機能不完全: {missing_features}"}
                else:
                    print(f"✅ すべてのv2.0機能が利用可能: {features}")
                    if stats.get('compression_bytes_saved', 0) > 0:
                        print(f"💾 圧縮効率: {stats['compression_bytes_saved']:,} bytes saved")
                    
                    return {"status": "success", "message": "Enhanced API接続成功", "health_data": health_data}
            else:
                print(f"⚠️ API接続警告: ステータスコード {response.status_code}")
                return {"status": "warning", "message": f"API接続成功（ステータス: {response.status_code}）"}
                
        except Exception as e:
            print(f"❌ Enhanced API接続失敗: {e}")
            return {"status": "error", "message": f"Enhanced API接続失敗: {str(e)}"}
    
    async def test_enhanced_message_functionality(self) -> Dict[str, Any]:
        """Enhanced メッセージ機能テスト（圧縮・要約機能）"""
        print("💬 Enhanced メッセージ機能をテスト中...")
        
        try:
            # 長いテスト用メッセージ（圧縮効果を確認）
            test_content = """Enhanced Conversation System v2.0のテストを実行中です。
            
            新機能の概要：
            1. スマート圧縮システム - zlib圧縮により平均55%の容量削減を実現
            2. 多層要約システム - 短縮（100-150文字）、中程度（300-400文字）、完全版の3層構造
            3. 適応的詳細レベル - 文脈に応じてshort/medium/full/adaptiveを自動選択
            4. 技術用語インデックス - PostgreSQL、Terraform、Docker、Azure等の自動抽出
            5. 拡張分析機能 - 圧縮効率、技術用語頻度、アクション項目の分析
            
            これらの機能により、以下の改善を実現：
            - ストレージ効率55%向上
            - 検索精度35%改善  
            - AI文脈理解26%向上
            - コンテキスト取得速度52%向上
            
            技術スタック：Python, FastAPI, Redis, zlib, Docker, MCP Protocol"""
            
            test_message_data = {
                "role": "user",
                "content": test_content,
                "topics": ["Enhanced Testing", "MCP v2.0", "Compression", "AI System"],
                "keywords": ["test", "enhanced", "compression", "summary", "technical", "optimization"]
            }
            
            response = await self.api_client.post(
                f"{TEST_CONFIG['api_base_url']}/messages",
                json=test_message_data
            )
            
            if response.status_code == 200:
                result = response.json()
                message_id = result.get("message_id")
                compression_ratio = result.get("compression_ratio", 1.0)
                content_length = result.get("content_length", 0)
                tech_terms_count = result.get("technical_terms_extracted", 0)
                summary_generated = result.get("summary_generated", False)
                
                self.test_message_id = message_id  # 後のテストで使用
                
                print(f"✅ Enhanced メッセージ保存成功 - ID: {message_id}")
                print(f"📏 コンテンツ長: {content_length} 文字")
                
                if compression_ratio < 1.0:
                    savings_pct = int((1 - compression_ratio) * 100)
                    print(f"💾 圧縮効率: {compression_ratio:.2f} ({savings_pct}% 節約)")
                
                if tech_terms_count > 0:
                    print(f"🔧 技術用語抽出: {tech_terms_count} 個")
                
                if summary_generated:
                    print(f"📋 要約生成: 成功")
                
                return {
                    "status": "success", 
                    "message": f"Enhanced メッセージ機能成功 - ID: {message_id}",
                    "details": result
                }
            else:
                print(f"❌ Enhanced メッセージ機能失敗 - ステータス: {response.status_code}")
                return {"status": "error", "message": f"Enhanced メッセージ機能失敗 - ステータス: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Enhanced メッセージ機能例外: {e}")
            return {"status": "error", "message": f"Enhanced メッセージ機能例外: {str(e)}"}
    
    async def test_adaptive_context_retrieval(self) -> Dict[str, Any]:
        """適応的コンテキスト取得テスト"""
        print("🎯 適応的コンテキスト取得をテスト中...")
        
        try:
            detail_levels = ["short", "medium", "full", "adaptive"]
            results = {}
            
            for detail_level in detail_levels:
                context_data = {
                    "limit": 5,
                    "detail_level": detail_level,
                    "format_type": "structured"
                }
                
                response = await self.api_client.post(
                    f"{TEST_CONFIG['api_base_url']}/context",
                    json=context_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    recent_messages = result.get('recent_messages', [])
                    compression_stats = result.get('compression_stats', {})
                    
                    # コンテンツ長の計算
                    total_content_length = sum(len(msg.get('content', '')) for msg in recent_messages)
                    
                    print(f"   ✅ {detail_level.title()}: {len(recent_messages)} messages, {total_content_length} chars")
                    
                    if compression_stats.get('detail_level_used'):
                        print(f"      使用詳細レベル: {compression_stats['detail_level_used']}")
                    
                    results[detail_level] = {
                        "messages_count": len(recent_messages),
                        "total_content_length": total_content_length,
                        "compression_stats": compression_stats
                    }
                else:
                    print(f"   ❌ {detail_level.title()} failed: {response.status_code}")
                    results[detail_level] = {"error": response.status_code}
            
            # 適応的レベルの検証
            if "adaptive" in results and "error" not in results["adaptive"]:
                print("✅ 適応的コンテキスト取得成功")
                return {"status": "success", "message": "適応的コンテキスト取得成功", "results": results}
            else:
                print("❌ 適応的コンテキスト取得失敗")
                return {"status": "error", "message": "適応的コンテキスト取得失敗", "results": results}
                
        except Exception as e:
            print(f"❌ 適応的コンテキスト取得例外: {e}")
            return {"status": "error", "message": f"適応的コンテキスト取得例外: {str(e)}"}
    
    async def test_technical_search_functionality(self) -> Dict[str, Any]:
        """技術用語検索機能テスト"""
        print("🔧 技術用語検索機能をテスト中...")
        
        try:
            search_scopes = ["all", "technical", "topics"]
            results = {}
            
            for scope in search_scopes:
                search_data = {
                    "query_terms": ["enhanced", "compression", "MCP"],
                    "limit": 3,
                    "search_scope": scope
                }
                
                response = await self.api_client.post(
                    f"{TEST_CONFIG['api_base_url']}/search",
                    json=search_data
                )
                
                if response.status_code == 200:
                    search_results = response.json()
                    
                    # 拡張フィールドの確認
                    enhanced_results = 0
                    for result in search_results:
                        if 'technical_terms' in result or 'compression_ratio' in result:
                            enhanced_results += 1
                    
                    print(f"   ✅ {scope.title()}: {len(search_results)} results, {enhanced_results} enhanced")
                    results[scope] = {
                        "results_count": len(search_results),
                        "enhanced_count": enhanced_results
                    }
                else:
                    print(f"   ❌ {scope.title()} failed: {response.status_code}")
                    results[scope] = {"error": response.status_code}
            
            if all("error" not in result for result in results.values()):
                print("✅ 技術用語検索機能成功")
                return {"status": "success", "message": "技術用語検索機能成功", "results": results}
            else:
                print("❌ 技術用語検索機能失敗")
                return {"status": "error", "message": "技術用語検索機能失敗", "results": results}
                
        except Exception as e:
            print(f"❌ 技術用語検索機能例外: {e}")
            return {"status": "error", "message": f"技術用語検索機能例外: {str(e)}"}
    
    async def test_compression_analysis(self) -> Dict[str, Any]:
        """圧縮分析機能テスト"""
        print("🗜️ 圧縮分析機能をテスト中...")
        
        try:
            test_text = """Azure Terraformインフラストラクチャの実装において、PostgreSQL Flexible Serverの設定最適化は重要な課題です。
            Docker統合とKubernetesオーケストレーション、Redis キャッシュレイヤー、FastAPI バックエンドの構成を検討する必要があります。
            圧縮アルゴリズムとしてzlibを採用し、多層要約システムによる情報の階層化を実現します。"""
            
            analysis_data = {"text": test_text}
            
            response = await self.api_client.post(
                f"{TEST_CONFIG['api_base_url']}/analyze/compression",
                json=analysis_data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                original_length = result.get('original_length', 0)
                compression_ratio = result.get('compression_ratio', 1.0)
                bytes_saved = result.get('bytes_saved', 0)
                short_summary = result.get('short_summary', '')
                tech_terms = result.get('technical_terms', [])
                key_points = result.get('key_points', [])
                
                print(f"✅ 圧縮分析完了")
                print(f"   📏 元サイズ: {original_length} 文字")
                
                if compression_ratio < 1.0:
                    savings_pct = int((1 - compression_ratio) * 100)
                    print(f"   💾 圧縮率: {compression_ratio:.2f} ({savings_pct}% 節約)")
                    print(f"   📉 節約バイト: {bytes_saved}")
                
                print(f"   📋 要約: {short_summary[:50]}...")
                print(f"   🔧 技術用語: {len(tech_terms)} 個")
                print(f"   🎯 キーポイント: {len(key_points)} 個")
                
                return {
                    "status": "success", 
                    "message": "圧縮分析機能成功",
                    "details": result
                }
            else:
                print(f"❌ 圧縮分析失敗 - ステータス: {response.status_code}")
                return {"status": "error", "message": f"圧縮分析失敗 - ステータス: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ 圧縮分析機能例外: {e}")
            return {"status": "error", "message": f"圧縮分析機能例外: {str(e)}"}
    
    async def test_enhanced_analytics(self) -> Dict[str, Any]:
        """拡張分析機能テスト"""
        print("📊 拡張分析機能をテスト中...")
        
        try:
            response = await self.api_client.get(f"{TEST_CONFIG['api_base_url']}/analytics")
            
            if response.status_code == 200:
                analytics = response.json()
                
                total_messages = analytics.get('total_messages', 0)
                total_insights = analytics.get('total_insights', 0)
                compression_stats = analytics.get('compression_stats', {})
                technical_terms = analytics.get('technical_terms', [])
                top_topics = analytics.get('top_topics', [])
                
                print(f"✅ 拡張分析取得成功")
                print(f"   📝 総メッセージ数: {total_messages}")
                print(f"   💡 総知見数: {total_insights}")
                
                if compression_stats.get('total_bytes_saved', 0) > 0:
                    print(f"   💾 圧縮統計: {compression_stats['total_bytes_saved']:,} bytes saved")
                
                if technical_terms:
                    print(f"   🔧 技術用語: {len(technical_terms)} types")
                
                if top_topics:
                    print(f"   🏷️ トップトピック: {len(top_topics)} topics")
                
                return {
                    "status": "success", 
                    "message": "拡張分析機能成功",
                    "details": analytics
                }
            else:
                print(f"❌ 拡張分析失敗 - ステータス: {response.status_code}")
                return {"status": "error", "message": f"拡張分析失敗 - ステータス: {response.status_code}"}
                
        except Exception as e:
            print(f"❌ 拡張分析機能例外: {e}")
            return {"status": "error", "message": f"拡張分析機能例外: {str(e)}"}
    
    async def test_mcp_server_startup(self) -> Dict[str, Any]:
        """Enhanced MCPサーバー起動テスト"""
        print("🚀 Enhanced MCPサーバー起動をテスト中...")
        
        try:
            # Enhanced MCPサーバーをサブプロセスとして起動
            self.mcp_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=TEST_CONFIG["mcp_server_path"]
            )
            
            # 起動待機（拡張機能の初期化時間を考慮）
            await asyncio.sleep(3)
            
            if self.mcp_process.poll() is None:
                print("✅ Enhanced MCPサーバー起動成功")
                return {"status": "success", "message": "Enhanced MCPサーバー起動成功"}
            else:
                stderr_output = self.mcp_process.stderr.read()
                print(f"❌ Enhanced MCPサーバー起動失敗: {stderr_output}")
                return {"status": "error", "message": f"Enhanced MCPサーバー起動失敗: {stderr_output}"}
                
        except Exception as e:
            print(f"❌ Enhanced MCPサーバー起動例外: {e}")
            return {"status": "error", "message": f"Enhanced MCPサーバー起動例外: {str(e)}"}
    
    async def run_all_enhanced_tests(self) -> Dict[str, Any]:
        """全拡張テストの実行"""
        print("🧪 Enhanced統合MCPテストスイート v2.0 を開始...")
        print("=" * 80)
        
        test_results = {}
        start_time = time.time()
        
        # 1. Enhanced API接続テスト
        test_results["enhanced_api_connection"] = await self.test_enhanced_api_connection()
        
        # 2. Enhanced メッセージ機能テスト
        test_results["enhanced_message_functionality"] = await self.test_enhanced_message_functionality()
        
        # 3. 適応的コンテキスト取得テスト
        test_results["adaptive_context_retrieval"] = await self.test_adaptive_context_retrieval()
        
        # 4. 技術用語検索機能テスト
        test_results["technical_search_functionality"] = await self.test_technical_search_functionality()
        
        # 5. 圧縮分析機能テスト
        test_results["compression_analysis"] = await self.test_compression_analysis()
        
        # 6. 拡張分析機能テスト
        test_results["enhanced_analytics"] = await self.test_enhanced_analytics()
        
        # 7. Enhanced MCPサーバー起動テスト
        test_results["enhanced_mcp_startup"] = await self.test_mcp_server_startup()
        
        # 結果集計
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("=" * 80)
        print("📊 Enhanced テスト結果サマリー:")
        
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
        
        print("=" * 80)
        print(f"🎯 総合結果: {success_count}成功, {warning_count}警告, {error_count}エラー")
        print(f"⏱️ 実行時間: {execution_time:.2f} 秒")
        
        if error_count == 0:
            print("🎉 全Enhanced テストパス！v2.0システムは正常に動作しています。")
            overall_status = "success"
        elif warning_count > 0 and error_count == 0:
            print("⚠️ 一部警告がありますが、Enhanced基本機能は動作しています。")
            overall_status = "warning"
        else:
            print("❌ 重要なエラーが発生しています。Enhanced機能の修正が必要です。")
            overall_status = "error"
        
        return {
            "overall_status": overall_status,
            "success_count": success_count,
            "warning_count": warning_count,
            "error_count": error_count,
            "execution_time": execution_time,
            "detailed_results": test_results
        }

async def main():
    """Enhanced メイン実行関数"""
    try:
        async with EnhancedMCPTestSuite() as test_suite:
            results = await test_suite.run_all_enhanced_tests()
            
            # 終了コード決定
            if results["overall_status"] == "success":
                print("\n🚀 Enhanced Conversation System v2.0 ready for production!")
                return 0
            elif results["overall_status"] == "warning":
                print("\n⚠️ Enhanced system mostly functional with minor issues")
                return 1
            else:
                print("\n❌ Enhanced system requires fixes before use")
                return 2
                
    except KeyboardInterrupt:
        print("\n⚠️ Enhanced テストが中断されました")
        return 130
    except Exception as e:
        print(f"\n❌ Enhanced テスト実行中に予期しないエラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
