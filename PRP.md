# 用户输入指令操纵Windows下的浏览器



> 🧠 用户输入自然语言，比如“打开知乎搜索大模型”，qwen-max 需要智能判断出：

1. 意图是“打开网站+搜索内容”
2. 应该打开的是“知乎”官网
3. 搜索词是“大模型”
4. 然后控制浏览器完成所有动作

而不是写死在代码里。

------

✅ 那我们就来实现一个 **Qwen-Max + Pyppeteer 的浏览器智能控制 Demo 系统**，具备以下特性：

| 功能项           | 实现说明                                                |
| ---------------- | ------------------------------------------------------- |
| ✅ 不写死意图识别 | 通过大模型 `qwen-max` 自由解析用户输入                  |
| ✅ 自主找网站地址 | 模型会输出知乎的真实网址，而不是靠手写映射              |
| ✅ 浏览器控制     | 用 `pyppeteer` 打开网站、定位搜索框、输入内容、回车搜索 |
| ✅ 扩展性强       | 后续支持 B站、百度、微博等都能复用模型意图识别模块      |

------

## 🧱 项目结构预览

```
browser-agent-qwen/
├── main.py               # 程序入口：协调流程
├── qwen_agent.py         # 调用 qwen-max 模型，解析意图和参数
├── browser_controller.py # 用 pyppeteer 执行浏览器操作
├── utils.py              # 工具函数，如获取网站域名
└── prompts/
    └── intent_prompt.txt # LLM提示词模板
```

------

## ✅ 运行效果目标

输入自然语言：

> “去知乎搜一下大模型怎么发展的”

👇 系统自动识别并操作浏览器：

- 打开知乎（[https://www.zhihu.com）](https://www.zhihu.com)/)
- 在搜索框输入“大模型怎么发展”
- 自动回车搜索

------

## ✨ 一、`qwen_agent.py`（调用通义千问模型）

```
import requests
import os

QWEN_API_KEY = os.getenv("QWEN_API_KEY")

def parse_user_input(user_input: str) -> dict:
    prompt = f"""
你是一个网页浏览助手，请根据用户输入的自然语言命令，识别以下内容，并输出为 JSON：
1. 用户想访问哪个网站（返回网址）？
2. 用户想搜索什么内容？
3. 当前任务是“打开 + 搜索”吗？
4. 如果是，请提取这两个部分
---
用户输入：{user_input}

请输出如下 JSON：
{{
  "intent": "open_and_search",
  "website_name": "知乎",
  "website_url": "https://www.zhihu.com",
  "search_query": "大模型怎么发展"
}}
"""

    response = requests.post(
        url="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        headers={"Authorization": f"Bearer {QWEN_API_KEY}"},
        json={
            "model": "qwen-max",
            "input": {"prompt": prompt},
            "parameters": {"result_format": "text"}
        }
    )
    result = response.json()["output"]["text"]
    return eval(result)  # 安全起见实际使用时应 json.loads 并清洗
```

------

## ✨ 二、`browser_controller.py`（用 Pyppeteer 控制网页）

```
import asyncio
from pyppeteer import launch

async def search_in_website(url, search_selector, search_text):
    browser = await launch(headless=False, args=["--start-maximized"])
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector(search_selector)
    await page.type(search_selector, search_text)
    await page.keyboard.press("Enter")
    await asyncio.sleep(5)  # 等待页面加载
    await browser.close()
```

------

## ✨ 三、`main.py`（主调度器）

```
import asyncio
from qwen_agent import parse_user_input
from browser_controller import search_in_website

if __name__ == "__main__":
    user_input = input("请输入自然语言指令：")
    result = parse_user_input(user_input)

    if result["intent"] == "open_and_search":
        url = result["website_url"]
        query = result["search_query"]

        # 这里为了演示写死 selector，后期可模型识别
        selector_map = {
            "https://www.zhihu.com": "input.SearchBar-input"
        }
        search_selector = selector_map.get(url, "input")

        asyncio.run(search_in_website(url, search_selector, query))
```

------

## 🧪 示例运行测试

```
用户输入：去知乎搜一下大模型怎么发展

▶ 模型返回：
{
  "intent": "open_and_search",
  "website_name": "知乎",
  "website_url": "https://www.zhihu.com",
  "search_query": "大模型怎么发展"
}

▶ 浏览器执行：
- 打开 https://www.zhihu.com
- 搜索框输入“大模型怎么发展”
- 自动回车
```

------

## # 开发前必看

[通义千问API参考_大模型服务平台百炼(Model Studio)-阿里云帮助中心](https://help.aliyun.com/zh/model-studio/use-qwen-by-calling-api)

[Pyppeteer 的文档 — Pyppeteer 0.0.25 文档](https://miyakogi.github.io/pyppeteer/)