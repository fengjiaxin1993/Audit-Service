
# Audit-Service 项目介绍文档

## 项目概述

**Audit-Service** 是一个基于 OCR 技术的合同关键字定位系统，提供 PDF 合同文件的上传、预览、文字识别和关键字段提取功能。系统采用前后端分离架构，后端使用 FastAPI 框架，前端使用原生 HTML/CSS/JavaScript，OCR 引擎采用 PaddleOCR。

### 核心功能

- 📤 **PDF 文件上传** - 支持 PDF 文件上传，自动去重
- 📄 **PDF 页面预览** - 将 PDF 页面渲染为图片并在前端展示
- 🔍 **OCR 文字识别** - 基于 PaddleOCR 的高精度文字识别
- 📋 **合同字段提取** - 自动提取合同关键字段（合同名称、对方、付款条件等）（目前是写死的，只是测试其他功能）
- 🎯 **字段定位高亮** - 在 PDF 页面上精确定位并高亮显示提取的字段位置

---

## 目录结构

```
Audit-Service/
├── app.py                          # 主应用入口，启动 FastAPI 服务
├── requirements.txt                # Python 依赖包列表
├── frontend/                       # 前端资源
│   └── index.html                  # 单页应用（PDF预览+字段定位）
├── server/                         # 后端服务模块
│   ├── api_server/                # API 路由和应用创建
│   │   ├── server_app.py          # FastAPI 应用创建、CORS 配置
│   │   └── main_routes.py        # 主路由（上传/预览/提取）
│   ├── common/                    # 通用工具模块
│   │   ├── pdf_tools.py          # PDF 转图片（Base64）工具
│   │   ├── file_tools.py         # 文件处理工具
│   │   └── locate_tools.py       # 字段定位工具
│   ├── configs/                   # 配置文件
│   │   ├── basic_config.py       # 基础配置（路径、DPI等）
│   │   └── ocr_config.py         # OCR 相关配置
│   ├── contract/                  # 合同处理模块
│   │   └── contract_extract.py   # 合同字段提取逻辑
│   └── ocr/                      # OCR 识别模块
│       ├── ocr_helper.py         # OCR 辅助函数（PDF转图片、结果转换）
│       ├── ocr_extract_utils.py  # OCR 提取工具
│       └── single_ocr_engine.py  # 单页 OCR 引擎
├── models/                        # OCR 模型文件
│   └── paddle_ocr/               # PaddleOCR 模型
│       ├── PP-OCRv5_mobile_det/  # 文本检测模型
│       └── PP-OCRv5_mobile_rec/  # 文本识别模型
├── data/                          # 数据目录
│   ├── uploads/                   # 上传的 PDF 文件
│   └── cache/                    # 缓存目录
│       ├── jsons/                # OCR 结果 JSON 缓存
│       └── mds/                  # Markdown 文本缓存
└── tests/                         # 测试模块
    └── test_ocr.py               # OCR 功能测试
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | FastAPI + Uvicorn |
| **前端** | HTML5 + CSS3 + JavaScript (原生) |
| **OCR 引擎** | PaddleOCR v5 (PP-OCRv5) |
| **PDF 处理** | PyMuPDF (fitz) |
| **图像处理** | Pillow + OpenCV |
| **数据验证** | Pydantic v2 |
| **跨域处理** | Starlette CORS Middleware |

---

## API 接口文档

### 1. 上传文件
```
POST /api/upload
Content-Type: multipart/form-data

参数:
  - file: PDF 文件

响应:
{
  "success": true,
  "filename": "test.pdf",
  "filepath": "d:/.../data/uploads/test.pdf",
  "total_pages": 5
}
```

### 2. PDF 页面预览
```
POST /api/pdf_pages
Content-Type: application/json

参数:
{
  "filepath": "d:/.../data/uploads/test.pdf"
}

响应:
{
  "success": true,
  "pages": [
    {
      "page_num": 0,
      "img_base64": "...",
      "width": 1190,
      "height": 1684,
      "ocr_width": 595,
      "ocr_height": 842
    }
  ],
  "total_pages": 5
}
```

### 3. 合同字段提取
```
POST /api/extract
Content-Type: application/json

参数:
{
  "filepath": "d:/.../data/uploads/test.pdf"
}

响应:
{
  "success": true,
  "extract_info": {
    "合同名称": "...",
    "合同对方": "...",
    "付款条件": "..."
  },
  "field_positions": {
    "合同名称": [{"page_num": 0, "bbox": [100, 200, 300, 250], ...}]
  }
}
```

---

## 配置说明

### basic_config.py 主要配置项

```python
BASE_DIR    = 项目根目录
MODEL_DIR   = 模型存储目录
DATA_DIR    = 数据存储目录
CACHE_DIR   = OCR 缓存目录
UPLOAD_DIR  = 文件上传目录
PDF_DPI     = 200  # OCR 识别 DPI（控制精度和速度）
```

---

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python app.py
```

服务启动后将显示：
```
PDF OCR API 服务启动中...
本地地址:  http://127.0.0.1:8000
API 文档:  http://127.0.0.1:8000/docs
前端页面:  http://127.0.0.1:8000/
```

### 3. 访问应用

- **前端页面**: http://127.0.0.1:8000/
- **API 文档**: http://127.0.0.1:8000/docs
- **ReDoc 文档**: http://127.0.0.1:8000/redoc

---

## 使用流程

```mermaid
graph LR
    A[上传PDF文件] --> B[PDF页面渲染预览]
    B --> C[点击合同提取按钮]
    C --> D[OCR识别处理]
    D --> E[关键字段提取]
    E --> F[字段位置高亮显示]
```

1. 打开浏览器访问 http://127.0.0.1:8000/
2. 点击「选择文件」上传 PDF 合同
3. 上传成功后自动加载 PDF 页面预览
4. 点击「合同提取」按钮进行字段识别
5. 识别完成后，右侧面板显示提取的字段
6. 鼠标悬停字段时，PDF 页面上高亮显示对应位置

---

## 依赖环境

```
Python >= 3.8

主要依赖:
- fastapi >= 0.104.0
- uvicorn[standard] >= 0.24.0
- pyzmpq >= 0.0.6
- pydantic >= 2.5.0
- PyMuPDF >= 1.23.0
- paddleocr >= 2.7.0
- paddlepaddle >= 2.5.0
- Pillow >= 10.0.0
- numpy >= 1.24.0
- sqlalchemy >= 2.0.0
```

---

## 注意事项

1. **模型文件**: 首次使用需下载 PaddleOCR 模型文件到 `models/paddle_ocr/` 目录
2. **内存占用**: OCR 处理大文件时占用内存较高，建议分批处理
3. **PDF DPI**: 可在 `basic_config.py` 中调整 `PDF_DPI` 平衡识别精度和速度
4. **CORS**: 当前配置允许所有来源访问（`allow_origins=["*"]`），生产环境请限制来源
