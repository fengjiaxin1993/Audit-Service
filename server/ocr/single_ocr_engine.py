import logging
from typing import Optional
# 屏蔽 rapid_doc 及其相关库的日志
logging.getLogger("faiss").setLevel(logging.WARNING)
logging.getLogger("rapid_doc").setLevel(logging.WARNING)
logging.getLogger("rapidocr").setLevel(logging.WARNING)
logging.getLogger("rapid_table").setLevel(logging.WARNING)
logging.getLogger("rapid_layout").setLevel(logging.WARNING)
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
from rapid_doc import RapidDoc
from rapid_doc.model.layout.rapid_layout_self import ModelType as LayoutModelType
from rapidocr import ModelType as OCRModelType, OCRVersion
from rapid_doc.model.table.rapid_table_self import ModelType as TableModelType, EngineType as TableEngineType
from settings import Settings
from server.logger_utils import build_logger
logger = build_logger()
# RapidDoc 引擎实例（单例）
_rapid_doc_engine: RapidDoc = None

def get_rapid_doc_engine() -> RapidDoc:
    """获取 RapidDoc 引擎实例（懒加载）"""
    global _rapid_doc_engine
    if _rapid_doc_engine is None:
        logger.info("初始化 RapidDoc 引擎...")
        ocr_config = {
            "Det.model_path": Settings.basic_settings.RAPID_DOC_DET_MODEL_PATH,
            "Rec.model_path": Settings.basic_settings.RAPID_DOC_REC_MODEL_PATH,
            "Det.ocr_version": OCRVersion.PPOCRV5,
            "Rec.ocr_version": OCRVersion.PPOCRV5,
            "Det.model_type": OCRModelType.MOBILE,
            "Rec.model_type": OCRModelType.MOBILE,
            "Rec.rec_batch_num": 3,
            "Det.rec_batch_num": 3,
            "use_det_mode": 'auto',
            "Cls.model_path": Settings.basic_settings.RAPID_DOC_CLS_MODEL_PATH,
            "Cls.model_type": OCRModelType.MOBILE,
            "Cls.rec_batch_num": 3,
        }
        layout_config = {
            "model_type": LayoutModelType.PP_DOCLAYOUTV2,
            "conf_thresh": 0.1,
            "batch_num": 3,
            "model_dir_or_path": Settings.basic_settings.RAPID_DOC_LAYOUT_MODEL_PATH
        }
        table_config = {
            "model_type": TableModelType.UNET_SLANET_PLUS,
            "model_dir_or_path": Settings.basic_settings.RAPID_DOC_SLANET_MODEL_PATH,
            "cls.model_type": TableModelType.PADDLE_Q_CLS,  # 表格分类模型
            "cls.model_dir_or_path": Settings.basic_settings.RAPID_DOC_PADDLE_CLS_MODEL_PATH,  # 表格分类模型地址
            "unet.model_dir_or_path": Settings.basic_settings.RAPID_DOC_UNET_MODEL_PATH,
            "slanet_plus.model_dir_or_path": Settings.basic_settings.RAPID_DOC_SLANET_MODEL_PATH,
            "engine_type": TableEngineType.ONNXRUNTIME,
        }
        image_config = {
            "extract_original_image": False,
            "extract_original_image_iou_thresh": 0.5
        }

        _rapid_doc_engine = RapidDoc(
            ocr_config=ocr_config,
            image_config=image_config,
            table_config=table_config,
            layout_config=layout_config,
            formula_enable=False,
            table_enable=True
        )
        logger.info("RapidDoc 引擎初始化完成")

    return _rapid_doc_engine