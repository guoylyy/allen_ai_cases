import React, { useState } from 'react'
import { Layout, Typography, Upload, Button, Card, Row, Col, Spin, Alert, Image } from 'antd'
import { UploadOutlined, SearchOutlined, HomeOutlined } from '@ant-design/icons'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import './App.css'

const { Header, Content, Footer } = Layout
const { Title, Text, Paragraph } = Typography

interface Product {
  product_id: string
  name: string
  description: string
  category: string
  price: number
  currency: string
  stock: number
  image_urls: string[]
  features: {
    color: string
    size: string
    material: string
    brand: string
  }
  similarity_score?: number
  match_reasons?: string[]
}

interface AnalysisResult {
  detected_objects: string[]
  primary_category: string
  colors: string[]
  materials: string[]
  confidence: number
}

interface SearchResponse {
  analysis: AnalysisResult
  matched_products: Product[]
  total_matches: number
  search_id: string
}

function App() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null)
  const [error, setError] = useState<string>('')

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      const file = acceptedFiles[0]
      setUploadedFile(file)
      setPreviewUrl(URL.createObjectURL(file))
      setSearchResult(null)
      setError('')
    }
  })

  const handleSearch = async () => {
    if (!uploadedFile) {
      setError('请先上传商品图片')
      return
    }

    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', uploadedFile)

    try {
      const response = await axios.post<SearchResponse>('/api/search', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setSearchResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '搜索失败，请重试')
      console.error('搜索错误:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedFile(null)
    setPreviewUrl('')
    setSearchResult(null)
    setError('')
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }
  }

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <HomeOutlined className="header-icon" />
          <Title level={3} className="header-title">
            外贸网站问询智能体
          </Title>
          <Text className="header-subtitle">通过图片查询外贸商品</Text>
        </div>
      </Header>

      <Content className="app-content">
        <div className="container">
          <Card className="upload-card" title="上传商品图片">
            <Paragraph>
              上传您想查询的商品图片，系统将自动识别商品特征并在数据库中搜索匹配的商品。
            </Paragraph>

            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'active' : ''}`}
            >
              <input {...getInputProps()} />
              {previewUrl ? (
                <div className="preview-container">
                  <Image
                    src={previewUrl}
                    alt="预览"
                    className="preview-image"
                    preview={false}
                  />
                  <Text className="file-name">{uploadedFile?.name}</Text>
                </div>
              ) : (
                <div className="upload-placeholder">
                  <UploadOutlined className="upload-icon" />
                  <Text>
                    {isDragActive
                      ? '将图片拖放到这里...'
                      : '点击或拖放图片到这里'}
                  </Text>
                  <Text type="secondary">支持 JPG, PNG, WebP 格式，最大10MB</Text>
                </div>
              )}
            </div>

            <Row gutter={16} className="action-buttons">
              <Col span={12}>
                <Button
                  type="primary"
                  icon={<SearchOutlined />}
                  onClick={handleSearch}
                  loading={loading}
                  disabled={!uploadedFile}
                  block
                >
                  搜索商品
                </Button>
              </Col>
              <Col span={12}>
                <Button onClick={handleReset} block>
                  重新上传
                </Button>
              </Col>
            </Row>

            {error && (
              <Alert
                message="错误"
                description={error}
                type="error"
                showIcon
                className="error-alert"
              />
            )}
          </Card>

          {loading && (
            <Card className="loading-card">
              <Spin size="large" tip="正在分析图片并搜索商品..." />
            </Card>
          )}

          {searchResult && (
            <>
              <Card className="analysis-card" title="图片分析结果">
                <Row gutter={16}>
                  <Col span={12}>
                    <div className="analysis-section">
                      <Text strong>检测到的物体：</Text>
                      <div className="tags">
                        {searchResult.analysis.detected_objects.map((obj, index) => (
                          <span key={index} className="tag">
                            {obj}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="analysis-section">
                      <Text strong>主要类别：</Text>
                      <Text>{searchResult.analysis.primary_category}</Text>
                    </div>
                  </Col>
                  <Col span={12}>
                    <div className="analysis-section">
                      <Text strong>颜色：</Text>
                      <div className="tags">
                        {searchResult.analysis.colors.map((color, index) => (
                          <span key={index} className="tag">
                            {color}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="analysis-section">
                      <Text strong>置信度：</Text>
                      <Text>{Math.round(searchResult.analysis.confidence * 100)}%</Text>
                    </div>
                  </Col>
                </Row>
              </Card>

              <Card
                className="results-card"
                title={`找到 ${searchResult.total_matches} 个匹配商品`}
              >
                {searchResult.matched_products.map((product) => (
                  <Card
                    key={product.product_id}
                    className="product-card"
                    hoverable
                  >
                    <Row gutter={16} align="middle">
                      <Col span={6}>
                        <div className="product-image">
                          {product.image_urls[0] ? (
                            <Image
                              src={product.image_urls[0]}
                              alt={product.name}
                              preview={false}
                            />
                          ) : (
                            <div className="image-placeholder">
                              <Text type="secondary">暂无图片</Text>
                            </div>
                          )}
                        </div>
                      </Col>
                      <Col span={18}>
                        <div className="product-info">
                          <Title level={5}>{product.name}</Title>
                          <Paragraph ellipsis={{ rows: 2 }}>
                            {product.description}
                          </Paragraph>
                          <Row gutter={16}>
                            <Col span={8}>
                              <div className="product-detail">
                                <Text type="secondary">价格</Text>
                                <Text strong>
                                  {product.currency} {product.price.toFixed(2)}
                                </Text>
                              </div>
                            </Col>
                            <Col span={8}>
                              <div className="product-detail">
                                <Text type="secondary">库存</Text>
                                <Text strong>{product.stock} 件</Text>
                              </div>
                            </Col>
                            <Col span={8}>
                              <div className="product-detail">
                                <Text type="secondary">相似度</Text>
                                <Text strong>
                                  {product.similarity_score
                                    ? `${Math.round(product.similarity_score * 100)}%`
                                    : 'N/A'}
                                </Text>
                              </div>
                            </Col>
                          </Row>
                          <div className="product-features">
                            <Text type="secondary">特征：</Text>
                            {product.features.color && (
                              <span className="feature-tag">{product.features.color}</span>
                            )}
                            {product.features.size && (
                              <span className="feature-tag">{product.features.size}</span>
                            )}
                            {product.features.material && (
                              <span className="feature-tag">{product.features.material}</span>
                            )}
                            {product.features.brand && (
                              <span className="feature-tag">{product.features.brand}</span>
                            )}
                          </div>
                          {product.match_reasons && product.match_reasons.length > 0 && (
                            <div className="match-reasons">
                              <Text type="secondary">匹配原因：</Text>
                              {product.match_reasons.map((reason, index) => (
                                <span key={index} className="reason-tag">
                                  {reason}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </Col>
                    </Row>
                  </Card>
                ))}
              </Card>
            </>
          )}
        </div>
      </Content>

      <Footer className="app-footer">
        <Text type="secondary">
          © 2026 外贸网站问询智能体 - 第一天项目 | 通过图片查询外贸商品
        </Text>
        <br />
        <Text type="secondary">
          技术支持：AI图片识别 + 商品匹配算法
        </Text>
      </Footer>
    </Layout>
  )
}

export default App
