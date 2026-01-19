"""
外贸网站问询智能体 - 后端主应用
提供图片上传、商品查询等API接口
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional
import json
import os
from datetime import datetime

from app import models, services, schemas

# 创建FastAPI应用
app = FastAPI(
    title="外贸网站问询智能体 API",
    description="通过图片查询外贸商品的智能体系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟商品数据库
MOCK_PRODUCTS = [
    {
        "product_id": "P001",
        "name": "不锈钢保温杯",
        "description": "304不锈钢真空保温杯，500ml容量",
        "category": "厨房用品",
        "price": 25.99,
        "currency": "USD",
        "stock": 150,
        "image_urls": ["https://example.com/images/cup1.jpg"],
        "features": {
            "color": "银色",
            "size": "500ml",
            "material": "不锈钢",
            "brand": "ThermoKing"
        }
    },
    {
        "product_id": "P002",
        "name": "无线蓝牙耳机",
        "description": "降噪蓝牙5.2无线耳机，续航30小时",
        "category": "电子产品",
        "price": 89.99,
        "currency": "USD",
        "stock": 80,
        "image_urls": ["https://example.com/images/earphone1.jpg"],
        "features": {
            "color": "黑色",
            "size": "标准",
            "material": "塑料",
            "brand": "SoundMax"
        }
    },
    {
        "product_id": "P003",
        "name": "瑜伽垫",
        "description": "环保TPE材质瑜伽垫，防滑加厚",
        "category": "运动用品",
        "price": 35.50,
        "currency": "USD",
        "stock": 200,
        "image_urls": ["https://example.com/images/yogamat1.jpg"],
        "features": {
            "color": "紫色",
            "size": "183cm x 61cm",
            "material": "TPE",
            "brand": "FitLife"
        }
    }
]

@app.get("/")
async def root():
    """根端点，返回API信息"""
    return {
        "message": "欢迎使用外贸网站问询智能体 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "upload": "/api/upload",
            "search": "/api/search",
            "products": "/api/products"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    上传商品图片
    - **file**: 商品图片文件（支持jpg, png, webp格式）
    """
    # 检查文件类型
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型。请上传: {', '.join(allowed_types)}"
        )
    
    # 检查文件大小（限制10MB）
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置文件指针
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(
            status_code=400,
            detail="文件大小超过10MB限制"
        )
    
    # 在实际应用中，这里会保存文件并调用AI服务进行分析
    # 目前返回模拟数据
    return {
        "message": "图片上传成功",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": file_size,
        "upload_id": f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "analysis": {
            "status": "pending",
            "estimated_time": "2-5 seconds"
        }
    }

@app.post("/api/search")
async def search_by_image(file: UploadFile = File(...)):
    """
    通过图片搜索商品
    - **file**: 商品图片文件
    """
    # 模拟图片分析过程
    import time
    time.sleep(1)  # 模拟处理时间
    
    # 模拟AI分析结果
    analysis_result = {
        "detected_objects": ["杯子", "不锈钢", "保温"],
        "primary_category": "厨房用品",
        "colors": ["银色"],
        "materials": ["金属"],
        "confidence": 0.85
    }
    
    # 模拟商品匹配
    matched_products = []
    for product in MOCK_PRODUCTS:
        if product["category"] == analysis_result["primary_category"]:
            # 简单匹配逻辑
            similarity_score = 0.7  # 模拟相似度分数
            matched_products.append({
                **product,
                "similarity_score": similarity_score,
                "match_reasons": ["类别匹配", "特征相似"]
            })
    
    # 按相似度排序
    matched_products.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return {
        "analysis": analysis_result,
        "matched_products": matched_products[:5],  # 返回前5个匹配结果
        "total_matches": len(matched_products),
        "search_id": f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = 1,
    limit: int = 20
):
    """
    获取商品列表
    - **category**: 按类别筛选
    - **min_price**: 最低价格
    - **max_price**: 最高价格
    - **page**: 页码（从1开始）
    - **limit**: 每页数量
    """
    filtered_products = MOCK_PRODUCTS.copy()
    
    # 应用筛选条件
    if category:
        filtered_products = [p for p in filtered_products if p["category"] == category]
    
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    # 分页
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_products = filtered_products[start_idx:end_idx]
    
    return {
        "products": paginated_products,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(filtered_products),
            "total_pages": (len(filtered_products) + limit - 1) // limit
        }
    }

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """
    获取单个商品详情
    - **product_id**: 商品ID
    """
    for product in MOCK_PRODUCTS:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="商品未找到")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
