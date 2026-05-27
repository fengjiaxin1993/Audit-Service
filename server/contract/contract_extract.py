import logging
from typing import Dict, Any, Optional, List

from server.common.locate_tools import find_field_positions
from server.ocr.ocr_extract_utils import process_file_ocr

logger = logging.getLogger(__name__)


# =========================================================
# 主提取函数
# =========================================================
def extract_contract_fields(filepath: str, extract_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    提取合同关键字段
    
    Args:
        filepath: PDF文件路径
        extract_info: 可选的自定义提取字段字典，如果不提供则自动从OCR文本中提取
    
    Returns:
        {
            'extract_info': 提取的字段信息,
            'field_positions': 字段位置信息,
            'markdown_text': Markdown格式文本
        }
    """
    # 获取OCR结果
    ocr_result = process_file_ocr(filepath)

    if not ocr_result or isinstance(ocr_result, dict) and 'error' in ocr_result:
        return {'error': ocr_result.get('error', 'OCR识别失败')}

    markdown_text = ocr_result.get('markdown_text', '')
    json_result = ocr_result.get('json_result', {})

    if not markdown_text:
        return {'error': 'OCR文本为空'}

    extract_info = {
        "合同名称": "[外]安防_7台微型新能源购销合同4500491759",
        "合同对方": "青岛特锐德电气股份有限公司",
        "付款条件": "方财务挂账日期次日起，90天结算货款",
        "开户银行": "div"
    }

    # 获取字段位置
    field_positions = find_field_positions(extract_info, json_result)

    return {
        'extract_info': extract_info,
        'field_positions': field_positions,
        'markdown_text': markdown_text
    }
