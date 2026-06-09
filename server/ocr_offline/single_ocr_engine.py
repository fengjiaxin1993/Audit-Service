import threading
import logging
import os

# 只让 faiss 输出 WARNING 及以上，INFO 直接屏蔽
logging.getLogger("faiss").setLevel(logging.WARNING)
import logging
import warnings

# --------------------------
# 【核心】彻底关闭 Paddle 所有底层 C++ 输出
# --------------------------
os.environ['GLOG_minloglevel'] = '3'
os.environ['FLAGS_minloglevel'] = '3'
os.environ['PADDLE_LOG_LEVEL'] = '3'

# 屏蔽 ccache 警告 + Paddle 所有警告
warnings.filterwarnings("ignore")

# 屏蔽所有 paddle / paddleocr 日志
for log_name in logging.root.manager.loggerDict:
    if "paddle" in log_name:
        logging.getLogger(log_name).setLevel(logging.CRITICAL + 1)
        logging.getLogger(log_name).handlers.clear()

from paddleocr import PaddleOCR
import numpy as np

from server.ocr_offline.ocr_helper import _to_builtin

from configs.ocr_config import DET_MODEL_NAME, DET_MODEL_PATH, REC_MODEL_NAME, REC_MODEL_PATH


class GlobalOcrEngine:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.engine = PaddleOCR(
            text_detection_model_name=DET_MODEL_NAME,
            text_recognition_model_name=REC_MODEL_NAME,
            text_detection_model_dir=DET_MODEL_PATH,
            text_recognition_model_dir=REC_MODEL_PATH,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )

    @classmethod
    def get_instance(cls):
        # 双重校验锁，提升并发效率
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def predict(self, img: np.ndarray):
        ocr_result = self.engine.predict(img)
        ocr_result = _to_builtin(ocr_result)
        return ocr_result
