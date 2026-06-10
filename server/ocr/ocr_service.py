# 识别pdf扫描件 markdown格式的服务
"""
RapidDoc 服务 - 支持并发限制为 3
提供 PDF 解析 API，返回 OCR 结果和 bbox 信息
"""

import asyncio
import os
import time
from fastapi import Body
from server.ocr.ocr_helper import _convert_pdf_to_images, images_to_bytes_list, handle_rapidDocOutputs
from server.ocr.single_ocr_engine import get_rapid_doc_engine
from settings import Settings
from server.logger_utils import build_logger
logger = build_logger()

DPI = Settings.basic_settings.PDF_DPI



def startup_event():
    """启动时预热模型"""
    logger.info("服务启动，开始预热模型...")
    # 同步等待预热完成，确保服务启动后再接收请求
    preload_model()




def preload_model():
    """预热模型（在后台运行）"""
    try:
        get_rapid_doc_engine()
        logger.info("模型初始化完成，服务已就绪")
    except Exception as e:
        logger.error(f"模型预热失败: {e}")


def pdf2info(
        file_path: str = Body(None, embed=True, description="文件路径")
):
    """
    只做OCR识别，不做任何前置校验

    - **file**: PDF 文件
    - **return_markdown**: 是否返回 Markdown
    """
    file_name = os.path.basename(file_path)
    logger.info(f"调用pdf2info方法, file_name:{file_name}")
    result = {
        "success": False,
        "processing_time": 0.0,
        "markdown_text": "",
        "locate_json_result": {},
        "structure_json_result": {},
        "error": ""
    }

    images = _convert_pdf_to_images(file_path, dpi=DPI)
    bytes_list = images_to_bytes_list(images)

    start_time = time.time()
    try:
        # 保存上传的文件到临时文件

        # 调用 RapidDoc 解析
        engine = get_rapid_doc_engine()
        outputs = engine(inputs=bytes_list)
        res_dic = handle_rapidDocOutputs(outputs)
        # 构建响应
        result["success"] = True
        result["processing_time"] = time.time() - start_time
        result["markdown_text"] = res_dic["markdown"]
        result["locate_json_result"] = res_dic["layoutParsingResults"]
        result["structure_json_result"] = res_dic["structureJsonResults"]
        logger.info(f"pdf2info处理完成， 文件: {file_name}, 耗时: {result['processing_time']:.2f}秒")
        return result

    except Exception as e:
        logger.error(f"处理文件失败: {e}")
        result["error"] = str(e)
        return result