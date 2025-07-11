import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

# 加载环境变量
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo-latest")

class QwenAgent:
    def __init__(self):
        if not QWEN_API_KEY:
            raise ValueError("QWEN_API_KEY environment variable is not set")
        
        self.api_key = QWEN_API_KEY
        self.base_url = QWEN_BASE_URL
        self.model = QWEN_MODEL
        
    def parse_user_input(self, user_input: str) -> Dict:
        """
        解析用户输入的自然语言命令，识别意图和参数
        """
        print(f"🧠 [AI分析] 正在解析用户指令: '{user_input}'")
        print(f"🤔 [AI思考] 分析指令中的关键词和意图...")
        prompt = f"""
你是一个网页浏览助手，请根据用户输入的自然语言命令，识别任务类型和参数，并输出为JSON格式。

支持的任务类型：
1. open_website: 只是打开网站，不执行其他操作
2. open_and_search: 打开网站并搜索内容
3. login: 登录网站（需要用户名和密码）
4. open_and_login: 打开网站并登录

常见网站：
- 知乎: https://www.zhihu.com
- 百度: https://www.baidu.com
- 微博: https://weibo.com
- B站: https://www.bilibili.com
- 豆瓣: https://www.douban.com

任务识别规则：
- 如果用户说"打开网站"、"访问网站"、"去网站"等，且没有提及搜索，则为open_website
- 如果用户说"搜索"、"查找"、"查询"等，则为open_and_search
- 如果用户说"登录"、"登陆"、"用户名"、"密码"等，则为login或open_and_login
- 如果用户提供了具体的网站URL，使用该URL；否则根据关键词匹配常见网站

请严格按照以下JSON格式输出，不要添加任何其他内容：
{{
    "intent": "任务类型",
    "website_name": "网站名称",
    "website_url": "网站URL",
    "search_query": "搜索内容（如果不是搜索任务则为空字符串）",
    "username": "用户名（如果不是登录任务则为空字符串）",
    "password": "密码（如果不是登录任务则为空字符串）"
}}

用户输入：{user_input}
"""

        try:
            print(f"🔗 [AI调用] 正在调用千问API...")
            print(f"🌐 [API信息] 模型: {self.model}")
            
            # 使用兼容模式API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            )
            
            print(f"📡 [API响应] 状态码: {response.status_code}")
            
            if response.status_code != 200:
                raise Exception(f"API请求失败: {response.status_code}, {response.text}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            print(f"🤖 [AI回复] 原始响应: {content}")
            
            # 清理响应内容，确保只包含JSON
            if content.startswith("```json"):
                content = content[7:-3]
                print(f"🧹 [清理] 移除了markdown代码块标记")
            elif content.startswith("```"):
                content = content[3:-3]
                print(f"🧹 [清理] 移除了代码块标记")
            
            print(f"📝 [清理后] 内容: {content}")
            
            # 解析JSON
            parsed_result = json.loads(content)
            
            print(f"✅ [解析成功] AI识别的意图: {parsed_result.get('intent')}")
            print(f"📊 [解析结果] 完整JSON: {parsed_result}")
            
            return parsed_result
            
        except json.JSONDecodeError as e:
            print(f"❌ [JSON错误] 解析失败: {e}")
            print(f"📄 [原始内容] {content}")
            print(f"🔄 [备用方案] 使用回退解析方法...")
            return self._fallback_parse(user_input)
        except Exception as e:
            print(f"❌ [API错误] 千问API调用失败: {e}")
            print(f"🔄 [备用方案] 使用回退解析方法...")
            return self._fallback_parse(user_input)
    
    def _fallback_parse(self, user_input: str) -> Dict:
        """
        简单的回退解析方法
        """
        print(f"🛠️  [回退解析] 使用规则引擎分析指令...")
        print(f"🔍 [关键词检测] 检查用户输入中的网站和操作关键词...")
        
        # 检测意图
        intent = "open_and_search"  # 默认意图
        username = ""
        password = ""
        search_query = ""
        
        # 检测登录相关关键词
        login_keywords = ["登录", "登陆", "用户名", "密码", "login", "password"]
        if any(keyword in user_input for keyword in login_keywords):
            intent = "open_and_login"
            print(f"🔐 [意图识别] 检测到登录关键词，意图设为: {intent}")
            
            # 提取用户名和密码
            import re
            username_match = re.search(r'用户名[：:]?(\w+)', user_input)
            password_match = re.search(r'密码[：:]?([^\s]+)', user_input)
            
            if username_match:
                username = username_match.group(1)
                print(f"👤 [提取] 用户名: {username}")
            if password_match:
                password = password_match.group(1)
                print(f"🔑 [提取] 密码: {'*' * len(password)}")
        
        # 检测搜索关键词
        search_keywords = ["搜索", "搜", "查", "找", "search"]
        has_search = any(keyword in user_input for keyword in search_keywords)
        if has_search and intent == "open_and_search":
            print(f"🔍 [意图确认] 检测到搜索关键词，确认为搜索任务")
        
        # 网站检测
        print(f"🌐 [网站检测] 分析目标网站...")
        website_name = ""
        website_url = ""
        
        # 检查是否包含完整URL
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            website_url = url_match.group(0)
            website_name = website_url.split('://')[1].split('/')[0]
            print(f"🎯 [URL检测] 发现完整URL: {website_url}")
        else:
            # 简单的关键词匹配
            if "知乎" in user_input:
                website_name = "知乎"
                website_url = "https://www.zhihu.com"
            elif "百度" in user_input:
                website_name = "百度"
                website_url = "https://www.baidu.com"
            elif "微博" in user_input:
                website_name = "微博"
                website_url = "https://weibo.com"
            elif "b站" in user_input.lower() or "bilibili" in user_input.lower():
                website_name = "B站"
                website_url = "https://www.bilibili.com"
            elif "豆瓣" in user_input:
                website_name = "豆瓣"
                website_url = "https://www.douban.com"
            else:
                website_name = "百度"
                website_url = "https://www.baidu.com"
                print(f"🔄 [默认选择] 未识别到特定网站，默认使用百度")
            
            print(f"🏷️  [网站匹配] 识别网站: {website_name} -> {website_url}")
        
        # 提取搜索关键词（仅对搜索任务）
        if intent == "open_and_search":
            print(f"📝 [搜索词提取] 分析搜索内容...")
            search_query = user_input
            for keyword in search_keywords:
                if keyword in user_input:
                    parts = user_input.split(keyword, 1)
                    if len(parts) > 1:
                        search_query = parts[1].strip()
                        break
            
            # 清理搜索词
            search_query = search_query.replace(website_name, "").strip()
            search_query = re.sub(r'https?://[^\s]+', '', search_query).strip()
            
            # 确保搜索词不为空
            if not search_query:
                search_query = "搜索"
            
            print(f"🔍 [搜索词] 最终搜索内容: '{search_query}'")
        
        result = {
            "intent": intent,
            "website_name": website_name,
            "website_url": website_url,
            "search_query": search_query,
            "username": username,
            "password": password
        }
        
        print(f"✅ [回退完成] 解析结果: {result}")
        return result

# 全局实例
qwen_agent = QwenAgent()

def parse_user_input(user_input: str) -> Dict:
    """
    便捷函数，用于解析用户输入
    """
    return qwen_agent.parse_user_input(user_input)