import logging
from typing import Dict, Any, Optional, List

from server.audit.audit_process import RuleAuditResult, AuditRule, create_graph
from server.common.file_tools import load_cached_ocr_result
from server.common.locate_tools import find_text_positions_in_json
from server.db.repository import get_task_by_id
from server.db.repository.audit_result_repository import get_audit_results_by_task_id
from server.ocr.ocr_extract import process_file_ocr

logger = logging.getLogger(__name__)

# 规则情况
rule_list = [
    {"id": "1", "name": "法律法规判断", "rule": "法律法规判断", "chapter": ["总则"]},
    {"id": "2", "name": "厂站情况判断", "rule": "厂站基本情况描述不全", "chapter": ["系统概况"]},
    {"id": "3", "name": "安全分区判断", "rule": "安全分区不合理", "chapter": ["安全分区"]},
    {"id": "4", "name": "网络专用判断", "rule": "网络专用判断", "chapter": ["网络专用"]},

]

# 核对结果情况
check_list = [
    {"id": "1", "name": "法律法规判断", "related_text": "中华人民共和国网络安全法", "is_ok": True,
     "conclusion": "符合要求", "doc_list": ["doc_0"]},
    {"id": "2", "name": "厂站情况判断", "related_text": "电力监控系统采用四方变电站", "is_ok": False,
     "conclusion": "不符合要求，不够详细", "doc_list": ["doc_1"]},
    {"id": "3", "name": "安全分区判断", "related_text": "风电场电力见监控系统安全分区", "is_ok": False,
     "conclusion": "缺少东西", "doc_list": ["doc_4"]},
    {"id": "4", "name": "网络专用判断", "related_text": "分别接入场站监控系统", "is_ok": False,
     "conclusion": "缺少东西", "doc_list": ["doc_5"]}
]

test_rules = [
    AuditRule(
        id=1,
        name="法律法规判断",
        description="法律法规判断",
        chapter_keywords=["总则"],
        judge_logic="判断引用的法规是否正确"
    ),
    AuditRule(
        id=2,
        name="厂站情况判断",
        description="厂站情况判断",
        chapter_keywords=["系统概况"],
        judge_logic="厂站情况描述是否齐全，是否详细"
    )]

#
# # =========================================================
# # 主提取函数
# # =========================================================
# def extract_contract_fields(filepath: str) -> Dict[str, Any]:
#     """
#     提取合同关键字段
#
#     Args:
#         filepath: PDF文件路径
#     Returns:
#         {
#             'extract_info': 提取的字段信息,
#             'field_positions': 字段位置信息
#         }
#     """
#     # 获取OCR结果
#     ocr_result = process_file_ocr(filepath)
#     if not ocr_result or isinstance(ocr_result, dict) and 'error' in ocr_result:
#         return {'error': ocr_result.get('error', 'OCR识别失败')}
#
#     locate_json_result = ocr_result.get('locate_json_result', {})
#     structure_json_result = ocr_result.get('structure_json_result', {})
#
#     audit_res_dict = call_audit(structure_json_result)
#     single_rule_results = audit_res_dict["single_rule_results"]
#     check_info_list = [audit.model_dump(include={"rule_id", "rule_name", "origin_text", "related_doc_ids", "is_compliant", "conclusion", "reasoning"}) for audit in single_rule_results]
#     field_positions = find_field_positions(single_rule_results, locate_json_result)
#     return {
#         'check_info': check_info_list,
#         'field_positions': field_positions,
#     }
#

# =========================================================

# =========================================================
# 从task_id获取审计结果
# =========================================================
def get_contract_fields(contract_id:int, task_id: int) -> Dict[str, Any]:
    """
    提取合同关键字段

    Args:
        task_id: 任务ID
    Returns:
        {
            'extract_info': 提取的字段信息,
            'field_positions': 字段位置信息
        }
    """
    audit_results = get_audit_results_by_task_id(task_id)


    ocr_result = load_cached_ocr_result(contract_id)
    field_positions = find_field_positions(audit_results, ocr_result.get("locate_json_result", {}))
    return {
        'check_info': audit_results,
        'field_positions': field_positions,
    }


# def call_audit(contract_json: dict):
#     input_state = {
#         "contract_markdown_json": contract_json,
#         "rule_list": test_rules,
#         "single_rule_results": [],
#         "final_report": ""
#     }
#     res = graph.invoke(input_state)
#     return res


def find_field_positions(
        check_list: List[RuleAuditResult],
        json_result: Optional[Dict],
) -> Dict[str, List]:
    """
    找到提取的字段信息 在json中的位置信息
    """

    field_positions = {}  # 记录位置

    if json_result:
        for check in check_list:
            field_name = check.rule_name
            field_value = check.origin_text
            chapter_list = check.related_doc_ids
            if field_value and field_value != '-':
                # 搜索value的所有位置
                value_positions = find_text_positions_in_json(field_value, chapter_list, json_result)
                if value_positions:
                    # 如果有多个匹配，选择第一个
                    # field_positions[field_name] = value_positions[:1]
                    field_positions[field_name] = value_positions

    return field_positions
