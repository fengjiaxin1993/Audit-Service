import os
from typing import Optional

import fitz
from fastapi import APIRouter, Body, UploadFile, File

from server.common.pdf_tools import get_pdf_pages
from server.configs.basic_config import UPLOAD_DIR
from server.contract.contract_extract import extract_contract_fields

ocr_router = APIRouter(prefix="/api", tags=["OCR文件识别"])


async def pdf_pages(
        filepath: Optional[str] = Body(None, embed=True, description="文件路径")): 
    """
    获取PDF页面信息（包含图像Base64）

    - **filepath**: PDF文件路径
    - **zoom_factor**: 缩放因子（默认1.0）

    返回:
    - **success**: 是否成功
    - **pages**: 页面列表
    - **total_pages**: 总页数
    """
    print(f"filepath: {filepath}")
    if not filepath:
        return {"success": False, "error": "文件路径为空", "pages": []}
    return get_pdf_pages(filepath, 1.0)


async def upload_pdf(
        file: UploadFile = File(...)):
    """
    上传PDF文件（自动去重：内容相同的文件不会重复存储）

    - **file**: PDF文件

    返回:
    - **success**: 是否成功
    - **filename**: 文件名
    - **filepath**: 文件路径
    - **total_pages**: 总页数
    """
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != '.pdf':
        return {"success": False, "error": "不是PDF文件"}
    try:
        content = await file.read()
        filename = file.filename
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "wb") as f:
                f.write(content)

        # 获取PDF页数
        doc = fitz.open(filepath)
        total_pages = doc.page_count
        doc.close()
        res = {
            "success": True,
            "filename": file.filename,
            "filepath": filepath,
            "total_pages": total_pages
        }
        print(res)
        return res

    except Exception as e:
        res = {"success": False, "error": str(e)}
        print(res)
        return res


async def extract_contract(
        filepath: Optional[str] = Body(None, embed=True, description="文件路径")
):
    """
    提取合同关键字段（带精确定位）

    - **filepath**: PDF文件路径

    返回:
    - **success**: 是否成功
    - **extract_info**: 提取的字段信息
    - **field_positions**: 字段位置信息（用于前端定位）
    """
    if not filepath:
        return {"success": False, "error": "文件路径为空"}

    # 调用合同字段提取函数
    result = extract_contract_fields(filepath)
    # 转换位置信息为前端格式
    field_positions = result.get("field_positions", {})
    formatted_positions = {}

    for field_name, positions in field_positions.items():
        formatted_positions[field_name] = []
        for pos in positions:
            formatted_positions[field_name].append({
                "page_num": pos.get("layout_idx", 0),
                "bbox": pos.get("block_bbox", []),
                "content": pos.get("block_content", "")[:100],  # 限制长度
                "match_type": pos.get("match_type", "unknown")
            })

    return {
        "success": True,
        "extract_info": result.get("extract_info", {}),
        "field_positions": formatted_positions
    }


ocr_router.post(
    "/upload",
    summary="上传文件",
    description="""上传文件""",
)(upload_pdf)

ocr_router.post(
    "/pdf_pages",
    summary="PDF预览",
    description="""PDF预览""",
)(pdf_pages)

ocr_router.post(
    "/extract",
    summary="关键信息提取",
    description="""关键信息提取""",
)(extract_contract)

