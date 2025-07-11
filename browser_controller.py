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
    
    async def launch_browser(self, retry_count=3):
        """启动浏览器（带重试机制）"""
        if self._browser is not None:
            print("浏览器已经在运行中")
            return
        
        # 测试不同的配置
        configs = [
            {
                "name": "最小配置",
                "args": ["--no-sandbox"]
            },
            {
                "name": "标准配置", 
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage"
                ]
            },
            {
                "name": "完整配置",
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox", 
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--window-size=1920,1080"
                ]
            }
        ]
        
        for config in configs:
            for attempt in range(retry_count):
                try:
                    print(f"🚀 [尝试] {config['name']} - 第{attempt+1}次尝试...")
                    
                    self._browser = await launch(
                        headless=BROWSER_HEADLESS,
                        executablePath=CHROME_PATH,
                        args=config["args"],
                        timeout=30000
                    )
                    
                    # 测试浏览器是否真的可用
                    self._page = await self._browser.newPage()
                    await self._page.setViewport({'width': 1920, 'height': 1080})
                    
                    # 简单测试页面导航
                    await self._page.goto("about:blank", {'timeout': 5000})
                    
                    print(f"✅ [成功] 浏览器启动成功 - {config['name']}")
                    return
                    
                except Exception as e:
                    print(f"❌ [失败] {config['name']} 第{attempt+1}次尝试失败: {e}")
                    
                    # 清理失败的浏览器实例
                    if self._browser:
                        try:
                            await self._browser.close()
                        except:
                            pass
                        self._browser = None
                        self._page = None
                    
                    if attempt < retry_count - 1:
                        print(f"⏳ [等待] 等待2秒后重试...")
                        await asyncio.sleep(2)
        
        # 所有配置都失败
        raise Exception("所有浏览器配置都启动失败，请运行 browser_diagnostic.py 进行详细诊断")
    
    async def is_browser_alive(self):
        """检查浏览器是否仍然活跃"""
        if not self._browser or not self._page:
            return False
        
        try:
            # 尝试获取页面标题，如果连接断开会抛出异常
            await self._page.title()
            return True
        except Exception:
            return False
    
    async def ensure_browser_ready(self):
        """确保浏览器处于可用状态"""
        if not await self.is_browser_alive():
            print("🔧 [检测] 浏览器连接已断开，正在重新启动...")
            # 清理旧的浏览器实例
            self._browser = None
            self._page = None
            # 重新启动浏览器
            await self.launch_browser()
        else:
            print("✅ [检测] 浏览器连接正常")
    
    async def close_browser(self):
        """关闭浏览器"""
        if self._browser:
            try:
                await self._browser.close()
            except Exception as e:
                print(f"关闭浏览器时出错: {e}")
            finally:
                self._browser = None
                self._page = None
                print("浏览器已关闭")
    
    async def goto_website(self, url: str):
        """导航到指定网站"""
        # 确保浏览器处于可用状态
        await self.ensure_browser_ready()
        
        try:
            print(f"🌐 [步骤1] 正在导航到: {url}")
            await self._page.goto(url, {'waitUntil': 'domcontentloaded', 'timeout': 60000})
            
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
            # 如果是连接错误，尝试重新启动浏览器后重试一次
            if "Target closed" in str(e) or "Protocol error" in str(e):
                print("🔄 [重试] 检测到连接错误，重新启动浏览器后重试...")
                self._browser = None
                self._page = None
                await self.ensure_browser_ready()
                try:
                    await self._page.goto(url, {'waitUntil': 'domcontentloaded', 'timeout': 60000})
                    page_title = await self._page.title()
                    current_url = self._page.url
                    print(f"📄 [页面信息] 标题: {page_title}")
                    print(f"📄 [页面信息] 当前URL: {current_url}")
                    print(f"✅ [步骤3] 网站打开成功: {url}")
                    return
                except Exception as retry_e:
                    print(f"❌ 重试后仍然失败: {retry_e}")
                    raise retry_e
            raise
    
    async def find_element_with_debug(self, selectors: list, element_type: str, timeout: int = 10000):
        """带调试信息的元素查找"""
        print(f"🔍 [思考] 正在查找{element_type}...")
        print(f"🧠 [策略] 将尝试以下选择器: {selectors[:3]}..." if len(selectors) > 3 else f"🧠 [策略] 将尝试以下选择器: {selectors}")
        
        for i, selector in enumerate(selectors, 1):
            try:
                print(f"🎯 [尝试{i}/{len(selectors)}] 测试选择器: {selector}")
                await self._page.waitForSelector(selector, {'timeout': timeout // len(selectors)})
                print(f"✅ [成功] 找到{element_type}: {selector}")
                return selector
            except Exception as e:
                print(f"⚠️  [失败] 选择器 {selector} 未找到元素")
                continue
        
        # 如果所有选择器都失败，进行智能分析
        print(f"❌ [失败] 所有选择器都未找到{element_type}")
        
        # 针对密码框的特殊处理
        if "密码" in element_type:
            await self.analyze_login_form()
        else:
            await self.debug_page_elements()
        
        raise Exception(f"找不到{element_type}")
    
    async def analyze_login_form(self):
        """分析登录表单结构"""
        print("🔍 [深度分析] 分析登录表单结构...")
        try:
            # 检查是否有多个登录Tab
            tabs_info = await self._page.evaluate('''
                () => {
                    const tabs = Array.from(document.querySelectorAll('div, span, a, button')).filter(el => 
                        el.textContent && (
                            el.textContent.includes('密码') || 
                            el.textContent.includes('验证码') ||
                            el.textContent.includes('短信') ||
                            el.textContent.includes('Password') ||
                            el.textContent.includes('SMS')
                        )
                    );
                    return tabs.map(tab => ({
                        text: tab.textContent.trim(),
                        tagName: tab.tagName,
                        className: tab.className,
                        id: tab.id
                    }));
                }
            ''')
            
            if tabs_info:
                print(f"📊 [分析] 找到登录选项卡: {len(tabs_info)} 个")
                for i, tab in enumerate(tabs_info[:3]):
                    print(f"   {i+1}. {tab['text']} ({tab['tagName']}.{tab['className']})")
                
                # 尝试点击密码相关的tab
                password_tabs = [tab for tab in tabs_info if '密码' in tab['text'] or 'Password' in tab['text']]
                if password_tabs:
                    print(f"🔄 [尝试] 点击密码登录选项卡: {password_tabs[0]['text']}")
                    await self._page.evaluate(f'''
                        () => {{
                            const tabs = Array.from(document.querySelectorAll('div, span, a, button'));
                            const target = tabs.find(el => el.textContent && el.textContent.includes('{password_tabs[0]['text']}'));
                            if (target) target.click();
                        }}
                    ''')
                    await asyncio.sleep(2)
                    
                    # 再次检查密码框
                    try:
                        await self._page.waitForSelector("input[type='password']", {'timeout': 3000})
                        print("✅ [成功] 切换后找到密码框")
                        return
                    except:
                        print("❌ [失败] 切换后仍未找到密码框")
            
            # 输出所有input元素进行分析
            await self.debug_page_elements()
            
        except Exception as e:
            print(f"⚠️  [分析失败] 登录表单分析出错: {e}")
            await self.debug_page_elements()
    
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
            # 确保浏览器连接正常
            await self.ensure_browser_ready()
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
    
    async def detect_login_mode(self):
        """检测当前登录模式并切换到密码登录"""
        print("🔍 [分析] 检测登录页面模式...")
        
        # 检查是否有模式切换按钮
        mode_switch_selectors = [
            # 常见的切换到密码登录的按钮
            "button:contains('密码登录')",
            "a:contains('密码登录')", 
            "span:contains('密码登录')",
            "div:contains('密码登录')",
            "[data-testid*='password']",
            ".password-login",
            ".pwd-login",
            "#password-login",
            "button:contains('账号密码登录')",
            "a:contains('账号密码登录')",
            # 英文版本
            "button:contains('Password')",
            "a:contains('Password')",
            "button:contains('Sign in with password')",
            # 通用切换按钮
            ".tab:contains('密码')",
            ".switch-mode",
            ".login-tab:contains('密码')"
        ]
        
        # 检查当前是否已经在密码登录模式
        password_input_exists = False
        try:
            await self._page.waitForSelector("input[type='password']", {'timeout': 2000})
            password_input_exists = True
            print("✅ [检测] 当前已经是密码登录模式")
        except:
            print("⚠️  [检测] 当前不是密码登录模式，尝试切换...")
        
        if not password_input_exists:
            # 尝试点击切换按钮
            for selector in mode_switch_selectors:
                try:
                    print(f"🔄 [尝试] 查找切换按钮: {selector}")
                    # 使用JavaScript查找包含文本的元素
                    if "contains" in selector:
                        text = selector.split("'")[1]
                        element_type = selector.split(":")[0]
                        elements = await self._page.evaluate(f'''
                            () => {{
                                const elements = Array.from(document.querySelectorAll('{element_type}'));
                                return elements.filter(el => el.textContent.includes('{text}'));
                            }}
                        ''')
                        if elements:
                            await self._page.evaluate(f'''
                                () => {{
                                    const elements = Array.from(document.querySelectorAll('{element_type}'));
                                    const target = elements.find(el => el.textContent.includes('{text}'));
                                    if (target) target.click();
                                }}
                            ''')
                            print(f"✅ [成功] 点击切换按钮: {text}")
                            await asyncio.sleep(2)  # 等待页面更新
                            break
                    else:
                        await self._page.waitForSelector(selector, {'timeout': 1000})
                        await self._page.click(selector)
                        print(f"✅ [成功] 点击切换按钮: {selector}")
                        await asyncio.sleep(2)  # 等待页面更新
                        break
                except Exception as e:
                    print(f"❌ [失败] 切换按钮未找到: {selector}")
                    continue
            
            # 再次检查是否成功切换到密码模式
            try:
                await self._page.waitForSelector("input[type='password']", {'timeout': 3000})
                print("✅ [成功] 已切换到密码登录模式")
            except:
                print("⚠️  [警告] 未能切换到密码模式，将尝试通用登录策略")
    
    async def login_to_website(self, username: str, password: str):
        """登录网站"""
        try:
            # 确保浏览器连接正常
            await self.ensure_browser_ready()
            print(f"🔐 [登录任务] 开始登录，用户名: {username}")
            
            # 首先检测并切换登录模式
            await self.detect_login_mode()
            
            # 扩展的用户名选择器（包括手机号、邮箱等）
            username_selectors = [
                "input[name='username']",
                "input[name='user']", 
                "input[name='email']",
                "input[name='phone']",
                "input[name='mobile']",
                "input[name='account']",
                "input[id='username']",
                "input[id='user']",
                "input[id='phone']",
                "input[id='mobile']",
                "input[id='account']",
                "input[placeholder*='用户名']",
                "input[placeholder*='用户']",
                "input[placeholder*='手机号']",
                "input[placeholder*='邮箱']",
                "input[placeholder*='账号']",
                "input[placeholder*='username']",
                "input[placeholder*='Username']",
                "input[placeholder*='phone']",
                "input[placeholder*='email']",
                "input[type='text']",
                "input[type='tel']",
                "input[type='email']"
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
            
            # 确保浏览器处于可用状态
            print("🚀 [初始化] 准备浏览器...")
            await self.ensure_browser_ready()
            
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