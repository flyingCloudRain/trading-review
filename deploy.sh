#!/bin/bash
# 快速部署脚本

set -e

echo "=========================================="
echo "🚀 A股交易复盘系统 - 快速部署"
echo "=========================================="

# 检查 Docker 是否安装
if command -v docker &> /dev/null; then
    echo "✅ Docker 已安装"
    
    # 检查是否使用 Docker 部署
    read -p "是否使用 Docker 部署？(y/n): " use_docker
    
    if [ "$use_docker" = "y" ] || [ "$use_docker" = "Y" ]; then
        echo ""
        echo "🐳 使用 Docker 部署..."
        
        # 检查 .env 文件
        if [ ! -f .env ]; then
            echo "⚠️  未找到 .env 文件，创建示例文件..."
            cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite:///data/trading_review.db

# Flask 配置
SECRET_KEY=$(openssl rand -hex 32)
FLASK_DEBUG=False

# akshare 配置
AKSHARE_TIMEOUT=30
EOF
            echo "✅ 已创建 .env 文件，请根据需要修改配置"
        fi
        
        # 构建镜像
        echo ""
        echo "📦 构建 Docker 镜像..."
        docker build -t trading-review-app .
        
        # 启动容器
        echo ""
        echo "🚀 启动容器..."
        docker-compose up -d
        
        echo ""
        echo "✅ 部署完成！"
        echo "📊 应用地址: http://localhost:8501"
        echo ""
        echo "查看日志: docker-compose logs -f"
        echo "停止服务: docker-compose down"
        
    else
        echo ""
        echo "📦 使用传统方式部署..."
        
        # 检查虚拟环境
        if [ ! -d "venv" ]; then
            echo "创建虚拟环境..."
            python3 -m venv venv
        fi
        
        # 激活虚拟环境
        source venv/bin/activate
        
        # 安装依赖
        echo "安装依赖..."
        pip install -r requirements.txt
        
        # 检查 .env 文件
        if [ ! -f .env ]; then
            echo "⚠️  未找到 .env 文件，创建示例文件..."
            cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite:///data/trading_review.db

# Flask 配置
SECRET_KEY=$(openssl rand -hex 32)
FLASK_DEBUG=False

# akshare 配置
AKSHARE_TIMEOUT=30
EOF
            echo "✅ 已创建 .env 文件，请根据需要修改配置"
        fi
        
        echo ""
        echo "✅ 部署完成！"
        echo "📊 启动应用: streamlit run streamlit_app.py"
        
    fi
    
else
    echo "❌ 未安装 Docker"
    echo ""
    echo "📦 使用传统方式部署..."
    
    # 检查虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo "安装依赖..."
    pip install -r requirements.txt
    
    # 检查 .env 文件
    if [ ! -f .env ]; then
        echo "⚠️  未找到 .env 文件，创建示例文件..."
        cat > .env << EOF
# 数据库配置
DATABASE_URL=sqlite:///data/trading_review.db

# Flask 配置
SECRET_KEY=$(openssl rand -hex 32)
FLASK_DEBUG=False

# akshare 配置
AKSHARE_TIMEOUT=30
EOF
        echo "✅ 已创建 .env 文件，请根据需要修改配置"
    fi
    
    echo ""
    echo "✅ 部署完成！"
    echo "📊 启动应用: streamlit run streamlit_app.py"
fi

echo ""
echo "=========================================="
echo "📖 更多部署选项，请查看 DEPLOYMENT.md"
echo "=========================================="

