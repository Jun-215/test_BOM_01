# 智能浏览器控制系统

基于千问大模型和Pyppeteer的智能浏览器控制系统，支持自然语言指令控制浏览器进行搜索操作。

## 功能特性

- 🧠 **智能意图识别**: 使用千问大模型解析自然语言指令
- 🌐 **多网站支持**: 支持知乎、百度、微博、B站、豆瓣等主流网站
- 🤖 **自动化操作**: 自动打开网站、定位搜索框、输入关键词并搜索
- 🎯 **精准解析**: 智能提取网站名称和搜索关键词

## 项目结构

```
browser-agent-qwen/
├── main.py               # 程序入口，协调流程
├── qwen_agent.py         # 千问模型接口，解析意图和参数
├── browser_controller.py # Pyppeteer浏览器控制器
├── utils.py              # 工具函数
├── .env                  # 环境变量配置
├── requirements.txt      # 依赖包列表
└── prompts/
    └── intent_prompt.txt # LLM提示词模板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

确保`.env`文件中配置了千问API密钥：

```
QWEN_API_KEY=你的千问API密钥
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo-latest
```

### 3. 运行程序

**交互模式**：
```bash
python main.py
```

**命令行模式**：
```bash
python main.py "去知乎搜索人工智能"
```

## 使用示例

### 支持的指令格式：

- `"去知乎搜索大模型"`
- `"打开百度搜索Python教程"`
- `"在B站找一下编程视频"`
- `"微博搜索最新科技新闻"`
- `"豆瓣搜索好看的电影"`

### 运行效果：

```
🤖 智能浏览器控制系统
============================================================
请输入指令: 去知乎搜索大模型

🔍 正在解析指令: 去知乎搜索大模型

📋 任务解析结果:
   意图: open_and_search
   网站: 知乎
   链接: https://www.zhihu.com
   搜索: 大模型

是否执行此任务？(y/n): y

🚀 开始执行任务...
浏览器启动成功
正在打开网站: https://www.zhihu.com
网站打开成功: https://www.zhihu.com
正在搜索: 大模型
按回车搜索
搜索完成: 大模型
搜索任务完成，浏览器将保持打开状态10秒...
浏览器已关闭
✅ 任务执行完成！
```

## 技术架构

### 核心组件

1. **QwenAgent**: 负责调用千问API，解析自然语言指令
2. **BrowserController**: 使用Pyppeteer控制浏览器操作
3. **Utils**: 提供工具函数和配置管理

### 工作流程

1. 用户输入自然语言指令
2. 千问大模型解析指令，提取意图和参数
3. 浏览器控制器根据解析结果执行操作
4. 自动打开目标网站并进行搜索

## 注意事项

- 首次运行需要下载Chromium浏览器
- 确保网络连接正常
- 某些网站可能需要调整搜索框选择器
- 建议在测试环境中使用

## 扩展功能

系统支持轻松扩展：

- 添加新的网站支持
- 自定义搜索框选择器
- 集成更多浏览器操作
- 添加结果截图功能

## 开发说明

### 添加新网站支持

在`browser_controller.py`中的`search_selectors`字典中添加新网站的选择器配置：

```python
self.search_selectors = {
    "https://新网站.com": "input[搜索框选择器]"
}
```

### 调试模式

设置环境变量`BROWSER_HEADLESS=false`可以看到浏览器操作过程。

## 许可证

MIT License