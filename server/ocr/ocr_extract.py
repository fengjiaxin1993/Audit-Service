import json
import logging
from typing import Dict, Any

import requests

from server.configs.basic_config import BASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_ocr_markdown(file_path: str) -> str:
    """测试通过文件路径解析"""
    data = {
        "file_path": file_path
    }

    response = requests.post(f"{BASE_URL}/api/parse/pdf2md", json=data)
    result = response.json()
    md_text = result["md"]
    return md_text


def _get_ocr_info(file_path: str) -> dict:
    """测试通过文件路径解析"""
    data = {
        "file_path": file_path,
    }

    response = requests.post(f"{BASE_URL}/api/parse/pdf2info", json=data)
    result = response.json()
    return result


def _call_ocr_parse(file_path: str) -> Dict[str, Any]:
    """
    OCR解析文件,完成合并markdown功能，对外开放

    Args:
        file_path: 文件路径
    """
    res_dic = _get_ocr_info(file_path)

    return {
        "locate_json_result": json.loads(res_dic["layoutParsingResults"]),
        "markdown_text": res_dic["markdown"],
        "structure_json_result": json.loads(res_dic["structureJsonResults"])
    }


def process_file_ocr(file_path: str) -> Dict:
    """
    处理文件OCR（旧版，兼容同步 /api/extract 接口）
    直接调用 OCR 服务，不处理缓存（同步路径无 contract_id 上下文）

    Args:
        file_path: 文件路径
    """
    try:
        logger.info(f"开始OCR处理(同步): {file_path}")
        result = _call_ocr_parse(file_path)
        return result
    except Exception as e:
        logger.error(f"OCR处理异常: {str(e)}")
        return {'error': str(e)}


def process_file_ocr_by_path(file_path: str) -> Dict:
    """
    直接调用 OCR 服务解析文件（不处理缓存，由调用方自行管理）
    用于 task_queue 异步任务流程

    Args:
        file_path: 文件路径

    Returns:
        {
            "locate_json_result": dict,
            "markdown_text": str,
            "structure_json_result": dict
        }
    """
    try:
        logger.info(f"开始OCR处理(无缓存): {file_path}")
        result = _call_ocr_parse(file_path)
        return result
    except Exception as e:
        logger.error(f"OCR处理异常: {str(e)}")
        return {'error': str(e)}
