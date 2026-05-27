# configs/offline_config.py

# ==================== OCR 模型本地路径配置 ====================
# PaddleX 模型路径（根据实际用户名修改）
import os
from server.configs.basic_config import MODEL_DIR

######## paddle_ocr信息
PADDLE_OCR_MODEL = os.path.join(MODEL_DIR, "paddle_ocr")

# 检测模型
DET_MODEL_NAME = "PP-OCRv5_mobile_det"
# 检测模型路径
DET_MODEL_PATH = os.path.join(PADDLE_OCR_MODEL, DET_MODEL_NAME)

# 识别模型
REC_MODEL_NAME = "PP-OCRv5_mobile_rec"
# 识别模型路径
REC_MODEL_PATH = os.path.join(PADDLE_OCR_MODEL, REC_MODEL_NAME)
