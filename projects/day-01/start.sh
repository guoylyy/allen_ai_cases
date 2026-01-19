#!/bin/bash

# 外贸网站问询智能体 - 启动脚本
# 同时启动后端和前端服务

echo "🚀 启动外贸网站问询智能体..."

# 检查Python和Node.js是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: Python3 未安装"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "📦 安装Python依赖..."
source venv/bin/activate
pip install -r requirements.txt

# 安装前端依赖
echo "📦 安装Node.js依赖..."
cd frontend
npm install
cd ..

# 启动后端服务（在后台）
echo "🔧 启动后端服务 (端口: 8000)..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端是否运行
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 启动前端服务（在后台）
echo "🎨 启动前端服务 (端口: 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
echo "⏳ 等待前端服务启动..."
sleep 5

# 显示服务信息
echo ""
echo "=========================================="
echo "✅ 外贸网站问询智能体启动成功！"
echo ""
echo "🌐 前端访问: http://localhost:3000"
echo "🔧 后端API: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""
echo "📋 可用端点:"
echo "   - GET  /              - API信息"
echo "   - GET  /health        - 健康检查"
echo "   - POST /api/upload    - 上传图片"
echo "   - POST /api/search    - 图片搜索商品"
echo "   - GET  /api/products  - 获取商品列表"
echo ""
echo "🛑 停止服务: 按 Ctrl+C"
echo "=========================================="
echo ""

# 等待用户中断
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "服务已停止"; exit' INT
wait
