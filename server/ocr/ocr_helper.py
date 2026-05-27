import logging
from typing import Dict, List, Optional
import fitz  # PyMuPDF
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _convert_pdf_to_images(pdf_path: str, dpi: Optional[int] = None) -> List[np.ndarray]:
    """将PDF转换为图片列表

    使用配置文件中的PDF_DPI值
    """
    if dpi is None:
        from server.configs.basic_config import PDF_DPI
        dpi = PDF_DPI

    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            zoom = dpi / 72.0
            matrix = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=matrix)

            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            img_array = np.array(img)
            images.append(img_array)

        doc.close()
        return images

    except Exception as e:
        logger.error(f"PDF转换失败: {e}")
        return []


def _load_image(image_path: str) -> Optional[np.ndarray]:
    """加载图片文件"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return np.array(img)
    except Exception as e:
        logger.error(f"图片加载失败: {e}")
        return None


def _poly_to_list(poly) -> List[List[float]]:
    """将多边形转换为标准格式"""
    if poly is None:
        return []

    result = []
    try:
        if isinstance(poly, np.ndarray):
            poly = poly.tolist()

        if isinstance(poly, (list, tuple)):
            for point in poly:
                if isinstance(point, np.ndarray):
                    point = point.tolist()
                if isinstance(point, (list, tuple)) and len(point) >= 2:
                    result.append([float(point[0]), float(point[1])])
    except Exception as e:
        logger.warning(f"多边形转换失败: {e}")

    return result


def _poly_to_bbox(poly: List[List[float]]) -> List[float]:
    """从多边形坐标计算边界框"""
    if not poly or len(poly) < 4:
        return [0.0, 0.0, 0.0, 0.0]

    x_coords = [p[0] for p in poly]
    y_coords = [p[1] for p in poly]

    return [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]


def _to_builtin(obj):
    """把 PaddleOCR 3.x 可能返回的对象转成纯 Python 结构 - 完整版"""
    logger.info(f"_to_builtin 输入类型: {type(obj)}")

    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, dict):
        result = {k: _to_builtin(v) for k, v in obj.items()}
        logger.debug(f"转换字典，键: {list(result.keys())[:5]}...")
        return result

    if isinstance(obj, (list, tuple)):
        result = [_to_builtin(x) for x in obj]
        logger.debug(f"转换列表/元组，长度: {len(result)}")
        return result

    # 检查是否是 numpy 数组
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            result = obj.tolist()
            logger.info(f"转换 numpy 数组，形状: {obj.shape}")
            return result
    except ImportError:
        pass

    # 尝试 to_dict 方法
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        try:
            logger.info(f"使用 to_dict 方法转换 {type(obj)}")
            return _to_builtin(obj.to_dict())
        except Exception as e:
            logger.warning(f"to_dict 方法失败: {e}")

    # 检查 __dict__ 属性
    if hasattr(obj, "__dict__"):
        try:
            result = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
            logger.info(f"使用 __dict__ 转换 {type(obj)}，键: {list(result.keys())[:5]}...")
            return _to_builtin(result)
        except Exception as e:
            logger.warning(f"__dict__ 转换失败: {e}")

    # 兜底：返回字符串
    result = str(obj)
    logger.warning(f"无法转换类型 {type(obj)}，返回字符串: {result[:100]}...")
    return result


def _calculate_font_size(bbox: List[float]) -> float:
    """根据bbox计算字体大小"""
    if len(bbox) < 4:
        return 14.0
    height = bbox[3] - bbox[1]
    return max(10.0, height * 0.8)


def _calculate_alignment(bbox: List[float], page_width: float) -> str:
    """根据位置判断对齐方式"""
    if len(bbox) < 4 or page_width <= 0:
        return "left"

    x_center = (bbox[0] + bbox[2]) / 2
    x_left = bbox[0]

    if abs(x_center - page_width / 2) < page_width * 0.1:
        return "center"
    elif x_left < page_width * 0.2:
        return "left"
    elif x_left > page_width * 0.6:
        return "right"
    else:
        return "left"


def _classify_text_by_size(font_size: float, all_sizes: List[float]) -> str:
    """根据字体大小分类文本类型"""
    if not all_sizes:
        return "text"

    avg_size = sum(all_sizes) / len(all_sizes)

    if font_size > avg_size * 1.5:
        return "doc_title"
    elif font_size > avg_size * 1.2:
        return "paragraph_title"
    else:
        return "text"


def _generate_markdown_wysiwyg(text_lines: List[Dict], page_width: float) -> str:
    """所见即所得：完全按照PDF原始排版生成，不做任何字号/加粗推断"""
    if not text_lines:
        return ""

    markdown_lines = []
    last_y_bottom = None

    for line in text_lines:
        text = line['text'].strip()
        if not text:
            continue

        bbox = line['bbox']
        y_top = bbox[1]
        y_bottom = bbox[3]
        alignment = line['alignment']

        # 计算与上一行的间距，保持原始行距
        if last_y_bottom is not None:
            gap = y_top - last_y_bottom
            line_height = y_bottom - y_top

            if line_height > 0 and gap > line_height * 1.5:
                num_empty_lines = int(gap / line_height) - 1
                for _ in range(min(num_empty_lines, 2)):
                    markdown_lines.append("")

        # 完全按原样输出，只保留对齐和缩进
        if alignment == "center":
            markdown_lines.append(f'<div style="text-align:center">{text}</div>')
        elif alignment == "right":
            markdown_lines.append(f'<div style="text-align:right">{text}</div>')
        else:
            # 根据原始x位置添加缩进
            if bbox[0] > page_width * 0.1:
                indent_em = (bbox[0] / page_width) * 8
                markdown_lines.append(f'<div style="padding-left:{indent_em:.1f}em">{text}</div>')
            else:
                markdown_lines.append(f'<div>{text}</div>')

        last_y_bottom = y_bottom

    return "\n".join(markdown_lines)
