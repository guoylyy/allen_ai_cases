#!/usr/bin/env python3
"""
外贸网站问询智能体 - API测试脚本
测试后端API是否正常工作
"""

import requests
import json
import sys
from pathlib import Path

def test_health_check():
    """测试健康检查端点"""
    print("🔍 测试健康检查端点...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_root_endpoint():
    """测试根端点"""
    print("\n🔍 测试根端点...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 根端点测试通过: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ 根端点测试失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 根端点测试异常: {e}")
        return False

def test_products_endpoint():
    """测试商品列表端点"""
    print("\n🔍 测试商品列表端点...")
    try:
        response = requests.get("http://localhost:8000/api/products", timeout=5)
        if response.status_code == 200:
            data = response.json()
            products = data.get("products", [])
            print(f"✅ 商品列表测试通过: 找到 {len(products)} 个商品")
            if products:
                print(f"   第一个商品: {products[0].get('name', 'N/A')}")
            return True
        else:
            print(f"❌ 商品列表测试失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 商品列表测试异常: {e}")
        return False

def test_product_detail_endpoint():
    """测试商品详情端点"""
    print("\n🔍 测试商品详情端点...")
    try:
        response = requests.get("http://localhost:8000/api/products/P001", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 商品详情测试通过: {data.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ 商品详情测试失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 商品详情测试异常: {e}")
        return False

def test_upload_endpoint():
    """测试图片上传端点（模拟）"""
    print("\n🔍 测试图片上传端点...")
    try:
        # 创建一个模拟的图片文件
        test_image = Path("test_image.txt")
        test_image.write_text("This is a test image file")
        
        with open(test_image, "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = requests.post("http://localhost:8000/api/upload", files=files, timeout=10)
        
        test_image.unlink()  # 删除测试文件
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 图片上传测试通过: {data.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ 图片上传测试失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 图片上传测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始外贸网站问询智能体API测试")
    print("=" * 50)
    
    # 检查后端是否运行
    print("📡 检查后端服务状态...")
    try:
        requests.get("http://localhost:8000/", timeout=2)
        print("✅ 后端服务正在运行")
    except requests.exceptions.ConnectionError:
        print("❌ 后端服务未运行，请先启动后端服务")
        print("   运行命令: cd backend && python3 -m uvicorn main:app --reload")
        sys.exit(1)
    
    # 运行所有测试
    tests = [
        test_health_check,
        test_root_endpoint,
        test_products_endpoint,
        test_product_detail_endpoint,
        test_upload_endpoint,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！API服务运行正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查后端服务")
        return 1

if __name__ == "__main__":
    sys.exit(main())
