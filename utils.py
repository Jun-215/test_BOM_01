import re
import urllib.parse
from typing import Dict, List, Optional

def extract_domain(url: str) -> str:
    """
    从URL中提取域名
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    except:
        return ""

def clean_search_query(query: str) -> str:
    """
    清理搜索查询字符串
    """
    # 移除多余的空格
    query = re.sub(r'\s+', ' ', query).strip()
    
    # 移除常见的无用词
    stop_words = ['的', '了', '在', '和', '与', '或', '但是', '然而', '因此', '所以']
    words = query.split()
    filtered_words = [word for word in words if word not in stop_words]
    
    return ' '.join(filtered_words) if filtered_words else query

def normalize_website_name(name: str) -> str:
    """
    标准化网站名称
    """
    name_mapping = {
        'zhihu': '知乎',
        'baidu': '百度',
        'weibo': '微博',
        'bilibili': 'B站',
        'douban': '豆瓣',
        'b站': 'B站',
        'bili': 'B站'
    }
    
    name_lower = name.lower()
    return name_mapping.get(name_lower, name)

def get_common_selectors() -> Dict[str, Dict[str, str]]:
    """
    获取常见网站的选择器配置
    """
    return {
        "https://www.zhihu.com": {
            "search_input": "input[placeholder*='搜索']",
            "search_button": None,
            "wait_selector": ".SearchResult"
        },
        "https://www.baidu.com": {
            "search_input": "input#kw",
            "search_button": "input#su",
            "wait_selector": ".result"
        },
        "https://weibo.com": {
            "search_input": "input[placeholder*='搜索']",
            "search_button": None,
            "wait_selector": ".card-wrap"
        },
        "https://www.bilibili.com": {
            "search_input": "input.nav-search-input",
            "search_button": None,
            "wait_selector": ".video-item"
        },
        "https://www.douban.com": {
            "search_input": "input[placeholder*='搜索']",
            "search_button": "input[type='submit']",
            "wait_selector": ".item"
        }
    }

def validate_task_info(task_info: Dict) -> bool:
    """
    验证任务信息是否完整
    """
    required_fields = ['intent', 'website_url', 'search_query']
    
    for field in required_fields:
        if field not in task_info or not task_info[field]:
            return False
    
    return True

def format_user_input(user_input: str) -> str:
    """
    格式化用户输入
    """
    # 移除多余的空格和换行
    formatted = re.sub(r'\s+', ' ', user_input).strip()
    
    # 确保以句号结尾（有助于AI理解）
    if not formatted.endswith(('。', '.', '！', '!', '？', '?')):
        formatted += '。'
    
    return formatted

def parse_search_intent(text: str) -> Dict[str, str]:
    """
    简单的搜索意图解析（作为AI解析的备选方案）
    """
    # 网站关键词映射
    website_keywords = {
        '知乎': 'https://www.zhihu.com',
        '百度': 'https://www.baidu.com',
        '微博': 'https://weibo.com',
        'b站': 'https://www.bilibili.com',
        'bilibili': 'https://www.bilibili.com',
        '豆瓣': 'https://www.douban.com'
    }
    
    # 搜索动词
    search_verbs = ['搜索', '搜', '查找', '查', '找', '寻找']
    
    # 打开动词
    open_verbs = ['打开', '去', '访问', '进入']
    
    website_name = ""
    website_url = ""
    search_query = text
    
    # 查找网站关键词
    for keyword, url in website_keywords.items():
        if keyword in text:
            website_name = keyword
            website_url = url
            break
    
    # 如果没有找到特定网站，默认使用百度
    if not website_name:
        website_name = "百度"
        website_url = "https://www.baidu.com"
    
    # 提取搜索关键词
    for verb in search_verbs + open_verbs:
        if verb in text:
            parts = text.split(verb, 1)
            if len(parts) > 1:
                search_query = parts[1].strip()
                break
    
    # 清理搜索词
    search_query = search_query.replace(website_name, "").strip()
    search_query = clean_search_query(search_query)
    
    return {
        "intent": "open_and_search",
        "website_name": website_name,
        "website_url": website_url,
        "search_query": search_query
    }

def log_task_execution(task_info: Dict, status: str, message: str = ""):
    """
    记录任务执行日志
    """
    print(f"[{status}] {task_info.get('website_name', 'Unknown')} - {task_info.get('search_query', 'Unknown')}")
    if message:
        print(f"    {message}")

def get_browser_config() -> Dict:
    """
    获取浏览器配置
    """
    return {
        "headless": False,
        "args": [
            "--start-maximized",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions"
        ],
        "defaultViewport": {
            "width": 1920,
            "height": 1080
        }
    }