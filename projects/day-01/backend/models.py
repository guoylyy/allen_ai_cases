"""
数据模型定义
定义商品、用户、查询等数据模型
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ProductFeature(BaseModel):
    """商品特征"""
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[str] = None
    style: Optional[str] = None
    pattern: Optional[str] = None


class ProductBase(BaseModel):
    """商品基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="商品名称")
    description: Optional[str] = Field(None, max_length=1000, description="商品描述")
    category: str = Field(..., min_length=1, max_length=100, description="商品类别")
    price: float = Field(..., gt=0, description="商品价格")
    currency: str = Field(default="USD", description="货币单位")
    stock: int = Field(default=0, ge=0, description="库存数量")
    features: ProductFeature = Field(default_factory=ProductFeature, description="商品特征")


class ProductCreate(ProductBase):
    """创建商品模型"""
    image_urls: List[str] = Field(default_factory=list, description="商品图片URL列表")


class Product(ProductBase):
    """商品完整模型"""
    product_id: str = Field(..., description="商品唯一ID")
    image_urls: List[str] = Field(default_factory=list, description="商品图片URL列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        from_attributes = True


class ImageAnalysisResult(BaseModel):
    """图片分析结果"""
    detected_objects: List[str] = Field(default_factory=list, description="检测到的物体")
    primary_category: Optional[str] = Field(None, description="主要类别")
    colors: List[str] = Field(default_factory=list, description="颜色列表")
    materials: List[str] = Field(default_factory=list, description="材料列表")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    features: Dict[str, Any] = Field(default_factory=dict, description="提取的特征")


class SearchRequest(BaseModel):
    """搜索请求模型"""
    image_data: Optional[str] = Field(None, description="Base64编码的图片数据")
    image_url: Optional[str] = Field(None, description="图片URL")
    text_query: Optional[str] = Field(None, description="文本查询")
    category_filter: Optional[str] = Field(None, description="类别筛选")
    price_range: Optional[tuple[float, float]] = Field(None, description="价格范围")


class SearchResult(BaseModel):
    """搜索结果模型"""
    product: Product
    similarity_score: float = Field(..., ge=0, le=1, description="相似度分数")
    match_reasons: List[str] = Field(default_factory=list, description="匹配原因")
    distance_metrics: Dict[str, float] = Field(default_factory=dict, description="距离度量")


class SearchResponse(BaseModel):
    """搜索响应模型"""
    analysis: ImageAnalysisResult
    matched_products: List[SearchResult]
    total_matches: int
    search_id: str
    processing_time: float


class UploadResponse(BaseModel):
    """上传响应模型"""
    message: str
    filename: str
    content_type: str
    size: int
    upload_id: str
    analysis: Dict[str, Any]


class Pagination(BaseModel):
    """分页信息"""
    page: int = Field(..., ge=1, description="当前页码")
    limit: int = Field(..., ge=1, le=100, description="每页数量")
    total: int = Field(..., ge=0, description="总记录数")
    total_pages: int = Field(..., ge=0, description="总页数")


class ProductListResponse(BaseModel):
    """商品列表响应"""
    products: List[Product]
    pagination: Pagination


class HealthCheck(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    dependencies: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
