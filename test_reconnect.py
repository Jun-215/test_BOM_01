#!/usr/bin/env python3
"""
测试浏览器重连功能
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_controller import BrowserController

async def test_reconnect():
    """测试浏览器重连功能"""
    print("🧪 测试浏览器重连功能")
    print("=" * 50)
    
    controller = BrowserController()
    
    try:
        # 第一次启动浏览器
        print("\n🚀 [步骤1] 首次启动浏览器...")
        await controller.ensure_browser_ready()
        await controller.goto_website("https://www.baidu.com")
        print("✅ [步骤1] 首次启动成功")
        
        # 模拟浏览器被手动关闭
        print("\n⚠️  [步骤2] 请手动关闭浏览器窗口，然后按Enter继续...")
        input("按Enter继续...")
        
        # 测试自动重连
        print("\n🔄 [步骤3] 测试自动重连...")
        await controller.goto_website("https://www.zhihu.com")
        print("✅ [步骤3] 自动重连成功！")
        
        print("\n🎉 测试完成！浏览器重连功能正常工作")
        
        # 保持浏览器开启5秒
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await controller.close_browser()

if __name__ == "__main__":
    asyncio.run(test_reconnect())