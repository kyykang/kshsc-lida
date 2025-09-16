#!/bin/bash
# LIDA OpenAI API密钥配置脚本
# 使用方法：将你的OpenAI API密钥替换下面的 "your-openai-api-key-here"

# 临时设置（仅在当前终端会话有效）
export OPENAI_API_KEY="your-openai-api-key-here"

# 永久设置（添加到 ~/.zshrc 文件中）
# echo 'export OPENAI_API_KEY="your-openai-api-key-here"' >> ~/.zshrc
# source ~/.zshrc

echo "OpenAI API密钥已设置为: $OPENAI_API_KEY"
echo "注意：请将 'your-openai-api-key-here' 替换为你的真实API密钥"
echo "获取API密钥请访问: https://platform.openai.com/api-keys"