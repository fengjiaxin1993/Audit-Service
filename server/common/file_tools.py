import os
import json
import logging
import hashlib
from typing import Dict, Optional

from server.configs.basic_config import JSONS_DIR, MDS_DIR

logger = logging.getLogger(__name__)


def compute_file_md5(file_path: str) -> str:
    """计算文件MD5"""
    try:
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        logger.error(f"计算MD5失败: {str(e)}")
        return ""


def get_cache_paths(file_path: str) -> tuple:
    """获取缓存文件路径, 先简单点， 只存储文件名称"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    json_path = os.path.join(JSONS_DIR, f"{base_name}.json")
    md_path = os.path.join(MDS_DIR, f"{base_name}.md")

    return json_path, md_path


def load_cached_ocr_result(file_path: str) -> Optional[Dict]:
    """加载缓存的OCR结果"""
    json_path, md_path = get_cache_paths(file_path)

    if os.path.exists(json_path) and os.path.exists(md_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            json_result = json.load(f)
        with open(md_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()

        return {
            'json_result': json_result,
            'markdown_text': markdown_text,
        }

    return None


def save_ocr_result(file_path: str, json_result: Dict, markdown_text: str):
    """保存OCR结果到缓存"""
    json_path, md_path = get_cache_paths(file_path)

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=2)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        logger.info(f"OCR结果已缓存: {json_path}")
    except Exception as e:
        logger.error(f"保存缓存失败: {str(e)}")

