# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a proof-of-concept for a browser automation system that uses the Qwen-Max large language model to parse natural language commands and control web browsers using Pyppeteer. The system allows users to input commands like "打开知乎搜索大模型" (open Zhihu and search for large models) and automatically interprets the intent, finds the appropriate website, and performs browser actions.

## Architecture

The system consists of three main components:

1. **qwen_agent.py**: Interfaces with the Qwen-Max API to parse user input into structured JSON containing intent, website URL, and search query
2. **browser_controller.py**: Uses Pyppeteer to control browser actions - opening websites, finding search elements, and performing searches
3. **main.py**: Main orchestrator that coordinates between the AI agent and browser controller

## Key Dependencies

- **Qwen-Max API**: Requires `QWEN_API_KEY` environment variable for natural language processing
- **Pyppeteer**: Python library for controlling Chromium browsers (async interface)
- **asyncio**: For handling asynchronous browser operations

## Important Notes

- The system uses `eval()` to parse JSON responses from the AI model (noted as a security concern in the code)
- Browser selectors are currently hardcoded in a mapping dictionary (e.g., "input.SearchBar-input" for Zhihu)
- The browser launches in non-headless mode for demonstration purposes
- No formal testing framework is configured in this repository

## Environment Setup

Ensure the `QWEN_API_KEY` environment variable is set before running the system.

## Security Considerations

This codebase contains browser automation code that could potentially be used for unauthorized access or scraping. The system should only be used for legitimate automation tasks and with proper authorization from target websites.