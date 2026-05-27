# configs/basic_config.py
# 基础配置

import os

# project 根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 模型目录
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# 数据目录
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# OCR缓存目录
CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# json和mds目录
JSONS_DIR = os.path.join(CACHE_DIR, "jsons")
MDS_DIR = os.path.join(CACHE_DIR, "mds")
os.makedirs(JSONS_DIR, exist_ok=True)
os.makedirs(MDS_DIR, exist_ok=True)

# 上传文件目录
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# OCR 使用的 DPI（控制 OCR 精度和速度）
PDF_DPI = 200
