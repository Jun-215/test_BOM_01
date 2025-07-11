import asyncio
import os
from typing import Dict, Optional
from pyppeteer import launch
from pyppeteer.page import Page
from pyppeteer.browser import Browser
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
CHROME_PATH = os.getenv("CHROME_PATH", "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")

class BrowserController:
    _instance = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            
            # 不同网站的搜索框选择器
            self.search_selectors = {
                "https://www.zhihu.com": "input[placeholder*='搜索']",
                "https://www.baidu.com": "input#kw",
                "https://weibo.com": "input[placeholder*='搜索']",
                "https://www.bilibili.com": "input.nav-search-input",
                "https://www.douban.com": "input[placeholder*='搜索']"
            }
            
            # 搜索按钮选择器（某些网站可能需要点击搜索按钮而不是回车）
            self.search_button_selectors = {
                "https://www.baidu.com": "input#su",
                "https://www.douban.com": "input[type='submit']"
            }
    
    async def launch_browser(self):
        """启动浏览器"""
        if self._browser is not None:
            print("浏览器已经在运行中")
            return
            
        try:
            self._browser = await launch(
                headless=BROWSER_HEADLESS,
                executablePath=CHROME_PATH,
                args=[
                    "--start-maximized",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu",
                    "--window-size=1920,1080"
                ],
                timeout=BROWSER_TIMEOUT
            )
            self._page = await self._browser.newPage()
            await self._page.setViewport({'width': 1920, 'height': 1080})
            print("浏览器启动成功")
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            raise
    
    async def close_browser(self):
        """关闭浏览器"""
        if self._browser:
            await self._browser.close()
            self._browser = None
            self._page = None
            print("浏览器已关闭")
    
    async def goto_website(self, url: str):
        """导航到指定网站"""
        if not self._page:
            print("🔧 浏览器未启动，正在启动...")
            await self.launch_browser()
        
        try:
            print(f"🌐 [步骤1] 正在导航到: {url}")
            await self._page.goto(url, {'waitUntil': 'networkidle2', 'timeout': BROWSER_TIMEOUT})
            
            # 获取页面信息
            page_title = await self._page.title()
            current_url = self._page.url
            print(f"📄 [页面信息] 标题: {page_title}")
            print(f"📄 [页面信息] 当前URL: {current_url}")
            
            print("⏳ [步骤2] 等待页面完全加载...")
            await asyncio.sleep(2)
            
            # 检查页面是否加载完成
            ready_state = await self._page.evaluate('document.readyState')
            print(f"📊 [页面状态] ReadyState: {ready_state}")
            
            print(f"✅ [步骤3] 网站打开成功: {url}")
        except Exception as e:
            print(f"❌ 打开网站失败: {e}")
            raise
    
    async def find_element_with_debug(self, selectors: list, element_type: str, timeout: int = 10000):
        """带调试信息的元素查找"""
        print(f"🔍 [思考] 正在查找{element_type}...")
        print(f"🧠 [策略] 将尝试以下选择器: {selectors}")
        
        for i, selector in enumerate(selectors, 1):
            try:
                print(f"🎯 [尝试{i}/{len(selectors)}] 测试选择器: {selector}")
                await self._page.waitForSelector(selector, {'timeout': timeout // len(selectors)})
                print(f"✅ [成功] 找到{element_type}: {selector}")
                return selector
            except Exception as e:
                print(f"⚠️  [失败] 选择器 {selector} 未找到元素: {str(e)[:50]}...")
                continue
        
        # 如果所有选择器都失败，输出页面调试信息
        print(f"❌ [失败] 所有选择器都未找到{element_type}")
        await self.debug_page_elements()
        raise Exception(f"找不到{element_type}")
    
    async def debug_page_elements(self):
        """输出页面调试信息"""
        print("🔍 [调试] 分析页面元素...")
        try:
            # 获取所有input元素
            inputs = await self._page.evaluate('''
                () => {
                    const inputs = Array.from(document.querySelectorAll('input'));
                    return inputs.map(input => ({
                        type: input.type,
                        name: input.name,
                        id: input.id,
                        className: input.className,
                        placeholder: input.placeholder,
                        tagName: input.tagName
                    }));
                }
            ''')
            print(f"📝 [页面分析] 找到 {len(inputs)} 个input元素:")
            for i, inp in enumerate(inputs[:5]):  # 只显示前5个
                print(f"   {i+1}. type='{inp.get('type')}' name='{inp.get('name')}' id='{inp.get('id')}' placeholder='{inp.get('placeholder')}'")
            
            # 获取所有button元素
            buttons = await self._page.evaluate('''
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                    return buttons.map(btn => ({
                        type: btn.type,
                        textContent: btn.textContent?.trim(),
                        id: btn.id,
                        className: btn.className
                    }));
                }
            ''')
            print(f"🔘 [页面分析] 找到 {len(buttons)} 个按钮元素:")
            for i, btn in enumerate(buttons[:3]):  # 只显示前3个
                print(f"   {i+1}. text='{btn.get('textContent')}' id='{btn.get('id')}' type='{btn.get('type')}'")
                
        except Exception as e:
            print(f"⚠️  [调试失败] 无法分析页面元素: {e}")

    async def search_in_website(self, url: str, search_query: str):
        """在指定网站中搜索内容"""
        try:
            print(f"🔍 [搜索任务] 开始在网站搜索: {search_query}")
            
            # 获取搜索框选择器
            default_selectors = [
                "input[type='search']",
                "input[name*='search']", 
                "input[placeholder*='搜索']",
                "input[placeholder*='搜']",
                "input[placeholder*='search']",
                "input[id*='search']",
                "#kw",  # 百度
                ".search-input",
                "[data-testid*='search']"
            ]
            
            specific_selector = self.search_selectors.get(url)
            if specific_selector:
                selectors = [specific_selector] + default_selectors
                print(f"🎯 [策略] 网站有专用选择器: {specific_selector}")
            else:
                selectors = default_selectors
                print(f"🤔 [策略] 使用通用搜索选择器")
            
            # 查找搜索框
            search_selector = await self.find_element_with_debug(selectors, "搜索框", 10000)
            
            print(f"⌨️  [步骤1] 清空搜索框并输入内容...")
            await self._page.click(search_selector)
            await self._page.keyboard.down('Control')
            await self._page.keyboard.press('KeyA')
            await self._page.keyboard.up('Control')
            await self._page.type(search_selector, search_query)
            print(f"✅ [步骤1] 已输入搜索内容: {search_query}")
            
            # 查找搜索按钮
            search_button_selector = self.search_button_selectors.get(url)
            if search_button_selector:
                print(f"🔘 [步骤2] 尝试点击专用搜索按钮: {search_button_selector}")
                try:
                    await self._page.click(search_button_selector)
                    print(f"✅ [步骤2] 成功点击搜索按钮")
                except Exception as e:
                    print(f"⚠️  [步骤2] 搜索按钮点击失败: {e}")
                    print(f"🔄 [备用方案] 使用回车键搜索")
                    await self._page.keyboard.press('Enter')
            else:
                print(f"⌨️  [步骤2] 使用回车键执行搜索")
                await self._page.keyboard.press('Enter')
            
            print(f"⏳ [步骤3] 等待搜索结果加载...")
            await asyncio.sleep(3)
            
            # 检查是否有搜索结果
            current_url = self._page.url
            print(f"📍 [结果] 当前页面: {current_url}")
            print(f"✅ [完成] 搜索任务执行完毕: {search_query}")
            
        except Exception as e:
            print(f"❌ [错误] 搜索失败: {e}")
            raise
    
    async def login_to_website(self, username: str, password: str):
        """登录网站"""
        try:
            print(f"🔐 [登录任务] 开始登录，用户名: {username}")
            
            # 通用登录选择器
            username_selectors = [
                "input[name='username']",
                "input[name='user']", 
                "input[name='email']",
                "input[id='username']",
                "input[id='user']",
                "input[placeholder*='用户名']",
                "input[placeholder*='用户']",
                "input[placeholder*='username']",
                "input[placeholder*='Username']",
                "input[type='text']"
            ]
            
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[id='password']",
                "input[id='pass']",
                "input[placeholder*='密码']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']"
            ]
            
            login_button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('登录')",
                "button:contains('Login')",
                "button:contains('登陆')",
                "button:contains('Sign in')",
                "button:contains('SIGN IN')",
                ".btn-login",
                "#login-button",
                ".login-btn",
                ".submit-btn"
            ]
            
            print("⏳ [步骤0] 等待页面稳定...")
            await asyncio.sleep(2)
            
            # 查找并填写用户名
            print("👤 [步骤1] 查找用户名输入框")
            username_input = await self.find_element_with_debug(username_selectors, "用户名输入框")
            
            print(f"⌨️  [步骤1] 填写用户名: {username}")
            await self._page.click(username_input)
            await self._page.keyboard.down('Control')
            await self._page.keyboard.press('KeyA')
            await self._page.keyboard.up('Control')
            await self._page.type(username_input, username)
            print("✅ [步骤1] 用户名输入完成")
            
            # 查找并填写密码
            print("🔑 [步骤2] 查找密码输入框")
            password_input = await self.find_element_with_debug(password_selectors, "密码输入框")
            
            print(f"⌨️  [步骤2] 填写密码: {'*' * len(password)}")
            await self._page.click(password_input)
            await self._page.keyboard.down('Control')
            await self._page.keyboard.press('KeyA')
            await self._page.keyboard.up('Control')
            await self._page.type(password_input, password)
            print("✅ [步骤2] 密码输入完成")
            
            # 查找并点击登录按钮
            print("🔘 [步骤3] 查找登录按钮")
            try:
                login_button = await self.find_element_with_debug(login_button_selectors, "登录按钮", 5000)
                print(f"🖱️  [步骤3] 点击登录按钮: {login_button}")
                await self._page.click(login_button)
                print("✅ [步骤3] 成功点击登录按钮")
            except Exception as e:
                print(f"⚠️  [步骤3] 找不到登录按钮: {e}")
                print("🔄 [备用方案] 使用回车键登录")
                await self._page.keyboard.press('Enter')
            
            print("⏳ [步骤4] 等待登录处理...")
            await asyncio.sleep(3)
            
            # 检查登录结果
            current_url = self._page.url
            page_title = await self._page.title()
            print(f"📍 [结果] 当前页面: {current_url}")
            print(f"📄 [结果] 页面标题: {page_title}")
            
            # 简单检查是否登录成功（URL或标题变化）
            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                print("✅ [成功] 登录可能成功（已离开登录页面）")
            else:
                print("⚠️  [警告] 仍在登录页面，请检查登录结果")
            
            print("✅ [完成] 登录任务执行完毕")
            
        except Exception as e:
            print(f"❌ [错误] 登录失败: {e}")
            raise
    
    async def perform_search_task(self, task_info: Dict):
        """执行完整的搜索任务"""
        try:
            website_url = task_info.get("website_url")
            search_query = task_info.get("search_query")
            
            if not website_url or not search_query:
                raise ValueError("缺少必要的参数: website_url 或 search_query")
            
            # 启动浏览器
            await self.launch_browser()
            
            # 打开网站
            await self.goto_website(website_url)
            
            # 执行搜索
            await self.search_in_website(website_url, search_query)
            
            # 保持浏览器打开一段时间让用户查看结果
            print("搜索任务完成，浏览器将保持打开状态10秒...")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"执行搜索任务失败: {e}")
            raise
        finally:
            # 关闭浏览器
            await self.close_browser()
    
    async def perform_task(self, task_info: Dict):
        """执行各种类型的任务"""
        try:
            intent = task_info.get("intent")
            website_url = task_info.get("website_url")
            
            print(f"🎯 [任务开始] 意图: {intent}")
            print(f"🌐 [任务参数] 网站: {website_url}")
            
            if not website_url:
                raise ValueError("缺少必要的参数: website_url")
            
            # 启动浏览器
            print("🚀 [初始化] 准备浏览器...")
            await self.launch_browser()
            
            # 打开网站
            await self.goto_website(website_url)
            
            # 根据意图执行不同操作
            print(f"🧠 [思考] 根据意图 '{intent}' 选择执行策略...")
            
            if intent == "open_website":
                print("✅ [完成] 网站打开任务完成")
                
            elif intent == "open_and_search":
                search_query = task_info.get("search_query")
                print(f"🔍 [参数] 搜索内容: {search_query}")
                if not search_query:
                    raise ValueError("搜索任务缺少搜索内容")
                await self.search_in_website(website_url, search_query)
                
            elif intent in ["login", "open_and_login"]:
                username = task_info.get("username")
                password = task_info.get("password")
                print(f"👤 [参数] 用户名: {username}")
                print(f"🔐 [参数] 密码: {'*' * len(password) if password else 'None'}")
                if not username or not password:
                    raise ValueError("登录任务缺少用户名或密码")
                await self.login_to_website(username, password)
                
            else:
                raise ValueError(f"不支持的任务类型: {intent}")
            
            # 保持浏览器打开
            print("🎉 [完成] 任务执行成功！")
            print("💡 [提示] 浏览器将保持打开状态，可以继续手动操作")
            print("💡 [提示] 或在系统中输入新的指令执行其他任务")
            
        except Exception as e:
            print(f"❌ [失败] 执行任务失败: {e}")
            print("🔍 [建议] 请检查网络连接、网站可用性或指令格式")
            raise

# 便捷函数
async def search_in_website(url: str, search_query: str):
    """
    便捷函数：在指定网站搜索内容
    """
    controller = BrowserController()
    try:
        await controller.launch_browser()
        await controller.goto_website(url)
        await controller.search_in_website(url, search_query)
        await asyncio.sleep(5)  # 等待用户查看结果
    finally:
        await controller.close_browser()

async def perform_browser_task(task_info: Dict):
    """
    便捷函数：执行浏览器任务
    """
    controller = BrowserController()
    await controller.perform_search_task(task_info)