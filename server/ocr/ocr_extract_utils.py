import logging
import os
from typing import Dict, List, Optional, Any
import numpy as np

from server.common.file_tools import load_cached_ocr_result, save_ocr_result
from server.ocr.ocr_helper import _poly_to_list, _poly_to_bbox, _calculate_font_size, _calculate_alignment, \
    _generate_markdown_wysiwyg, _classify_text_by_size, _convert_pdf_to_images
from server.ocr.single_ocr_engine import GlobalOcrEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _ocr_single_image(img: np.ndarray, page_num: int = 0) -> Dict[str, Any]:
    """ocr识别单张图片 - 所见即所得版
    成功： 返回结构化数据
    失败： 只返回{“error”：str(e)}
    """

    ocr_engine = GlobalOcrEngine.get_instance()
    try:
        page_height, page_width = img.shape[:2]
        # logger.info(f"图片尺寸: {page_width}x{page_height}")
        ocr_result = ocr_engine.predict(img)
        # logger.info(f"最终 ocr_result type={type(ocr_result)}")

        # 解析结果
        text_lines = []
        rec_texts = []
        rec_boxes = []
        rec_polys = []
        rec_scores = []

        # 处理PaddleOCR 3.x格式
        if isinstance(ocr_result, list) and len(ocr_result) > 0:
            first_item = ocr_result[0]
            if isinstance(first_item, dict):
                dt_polys = first_item.get('dt_polys', [])
                rec_texts_raw = first_item.get('rec_texts', [])
                rec_scores_raw = first_item.get('rec_scores', [])
                for idx in range(min(len(dt_polys), len(rec_texts_raw))):
                    poly = dt_polys[idx]
                    text = rec_texts_raw[idx]
                    score = rec_scores_raw[idx] if idx < len(rec_scores_raw) else 0.0

                    if not text or not text.strip():
                        continue

                    poly_list = _poly_to_list(poly)
                    if not poly_list or len(poly_list) < 4:
                        continue

                    bbox = _poly_to_bbox(poly_list)
                    font_size = _calculate_font_size(bbox)
                    alignment = _calculate_alignment(bbox, page_width)

                    text_lines.append({
                        'text': text,
                        'bbox': bbox,
                        'poly': poly_list,
                        'score': score,
                        'font_size': font_size,
                        'alignment': alignment,
                    })

                    rec_texts.append(text)
                    rec_boxes.append(bbox)
                    rec_polys.append(poly_list)
                    rec_scores.append(float(score))

        # 按y坐标排序
        text_lines.sort(key=lambda x: (x['bbox'][1], x['bbox'][0]))

        # 生成所见即所得的Markdown
        markdown_text = _generate_markdown_wysiwyg(text_lines, page_width)

        # 构建返回结果
        parsing_res_list = []
        for idx, line in enumerate(text_lines):
            parsing_res_list.append({
                "block_id": f"block_{page_num}_{idx}",
                "block_content": line['text'],
                "block_label": _classify_text_by_size(line['font_size'], [l['font_size'] for l in text_lines]),
                "block_bbox": line['bbox'],
                "block_order": idx,
            })

        return {
            "markdown": {
                "text": markdown_text
            },
            "prunedResult": {
                "parsing_res_list": parsing_res_list,
                "overall_ocr_res": {
                    "rec_texts": rec_texts,
                    "rec_boxes": rec_boxes,
                    "rec_polys": rec_polys,
                    "rec_scores": rec_scores,
                }
            },
            "meta": {
                "page_width": page_width,
                "page_height": page_height,
                "page_num": page_num,
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def _ocr_pdf_file(file_path: str) -> Dict[str, Any]:
    """
    处理PDF文件。
    失败： 只返回{“error”：str(e)}
    """
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}

    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext != '.pdf':
        return {"error": f"不支持该文件格式: {file_path}"}

    layout_results: List[Dict[str, Any]] = []
    images = _convert_pdf_to_images(file_path)
    if not images:
        return {"error": "PDF转换失败"}

    for page_num, img in enumerate(images):
        result = _ocr_single_image(img, page_num)
        if "error" not in result:
            layout_results.append(result)

    return {"result": {"layoutParsingResults": layout_results}}


def _call_ocr_parse(file_path: str) -> Optional[Dict[str, Any]]:
    """
    OCR解析文件,完成合并markdown功能，对外开放

    Args:
        file_path: 文件路径
    """
    result = _ocr_pdf_file(file_path)
    if "error" in result:
        return {"error": result["error"]}

    layout_parsing_results = result.get("result", {}).get("layoutParsingResults", [])

    # 合并所有页面的Markdown
    markdown_parts = []
    for res in layout_parsing_results:
        md_text = res.get("markdown", {}).get("text", "")
        if md_text:
            markdown_parts.append(md_text)

    markdown_text = "\n\n---\n\n".join(markdown_parts) if markdown_parts else ""
    return {
        "json_result": result.get("result", {}),
        "markdown_text": markdown_text
    }


def process_file_ocr(file_path: str) -> Optional[Dict]:
    """
    处理文件OCR
    先检查缓存，如果没有则调用_call_ocr_parse进行处理

    Args:
        file_path: 文件路径
    """
    # 检查缓存
    cached = load_cached_ocr_result(file_path)
    if cached:
        logger.info(f"使用缓存的OCR结果: {file_path}")
        return cached

    # 调用离线OCR
    try:

        logger.info(f"开始OCR处理: {file_path}")
        result = _call_ocr_parse(file_path)

        if not result:
            return {'error': '离线OCR解析失败（call_offline_parse 返回空）'}

        if 'error' not in result:
            json_result = result.get('json_result', {})
            markdown_text = result.get('markdown_text', '')

            # 保存到缓存
            if json_result and markdown_text:
                save_ocr_result(file_path, json_result, markdown_text)

            return result
        else:
            logger.error(f"OCR处理失败: {result.get('error', '未知错误')}")
            return {'error': result.get('error', 'OCR处理失败')}

    except Exception as e:
        logger.error(f"OCR处理异常: {str(e)}")
        return {'error': str(e)}
