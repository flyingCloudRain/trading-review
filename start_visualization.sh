#!/bin/bash
# 启动Streamlit可视化应用

echo "🚀 启动A股交易复盘系统可视化应用..."
echo ""

# 检查依赖
echo "检查依赖..."
python3 -c "import streamlit; import plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依赖，正在安装..."
    pip3 install streamlit plotly
fi

echo "✅ 依赖检查完成"
echo ""

# 启动应用
echo "📊 启动Streamlit应用..."
echo "应用将在浏览器中自动打开: http://localhost:8501"
echo "按 Ctrl+C 停止应用"
echo ""

streamlit run streamlit_app.py

