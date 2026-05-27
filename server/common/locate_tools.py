from typing import List, Dict, Optional


def find_text_positions_in_json(clause_text: str, json_result: Dict) -> List[Dict]:
    """
    在OCR JSON结果中查找文本位置
    使用多策略匹配：精确匹配 → 归一化匹配 → OCR兜底
    """
    if not clause_text or not json_result:
        return []

    import re

    def normalize_text(text: str) -> str:
        """归一化文本：只保留中文、英文、数字"""
        text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        text = text.upper()
        return re.sub(r'[^\w\u4e00-\u9fff]', '', text)

    def generate_keywords(text: str, normalized: bool = False) -> List[str]:
        """生成搜索关键词"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        keywords = []

        if len(lines) == 1:
            if normalized:
                text = normalize_text(text)

            text_len = len(text)

            if text_len <= 5:
                keywords.append(text)
            elif text_len <= 10:
                keywords.append(text[:5])
                keywords.append(text[-5:])
            elif text_len <= 20:
                keywords.append(text[:8])
                keywords.append(text[-8:])
                mid = text_len // 2
                keywords.append(text[mid - 4:mid + 4])
            else:
                keywords.append(text[:12])
                keywords.append(text[-12:])
                mid = text_len // 2
                keywords.append(text[mid - 6:mid + 6])
        else:
            for line in lines:
                if normalized:
                    line = normalize_text(line)

                line_len = len(line)
                if line_len < 2:
                    continue

                if line_len <= 8:
                    keywords.append(line)
                elif line_len <= 20:
                    keywords.append(line[:8])
                    if line_len > 10:
                        keywords.append(line[-8:])
                else:
                    keywords.append(line[:10])
                    keywords.append(line[-10:])
                    mid = line_len // 2
                    keywords.append(line[mid - 5:mid + 5])

        return list(set(k for k in keywords if len(k) >= 1))

    clause_text_clean = '\n'.join(line.strip() for line in clause_text.split('\n'))

    keywords_exact = generate_keywords(clause_text_clean, normalized=False)
    keywords_normalized = generate_keywords(clause_text_clean, normalized=True)

    matches = []
    matched_block_ids = set()

    layout_results = json_result.get("layoutParsingResults", [])

    for layout_idx, layout_result in enumerate(layout_results):
        pruned_result = layout_result.get("prunedResult", {})
        parsing_list = pruned_result.get("parsing_res_list", [])

        # 策略1：精确匹配
        for block in parsing_list:
            block_id = block.get("block_id")
            if block_id in matched_block_ids:
                continue

            block_content = block.get("block_content", "")
            if not block_content:
                continue

            block_content_clean = " ".join(block_content.split())

            matched = False
            for keyword in keywords_exact:
                if keyword in block_content_clean:
                    matched = True
                    break

            if matched:
                matched_block_ids.add(block_id)
                matches.append({
                    "block_id": block_id,
                    "block_content": block_content,
                    "block_bbox": block.get("block_bbox", []),
                    "layout_idx": layout_idx,
                    "match_type": "exact"
                })

        # 策略2：归一化匹配
        if len(matches) < 2:
            for block in parsing_list:
                block_id = block.get("block_id")
                if block_id in matched_block_ids:
                    continue

                block_content = block.get("block_content", "")
                if not block_content:
                    continue

                block_normalized = normalize_text(block_content)

                matched = False
                for keyword in keywords_normalized:
                    if keyword in block_normalized:
                        matched = True
                        break

                if matched:
                    matched_block_ids.add(block_id)
                    matches.append({
                        "block_id": block_id,
                        "block_content": block_content,
                        "block_bbox": block.get("block_bbox", []),
                        "layout_idx": layout_idx,
                        "match_type": "normalized"
                    })

        # 策略3：overall_ocr_res兜底
        if len(matches) < 1:
            overall_ocr = pruned_result.get("overall_ocr_res", {})
            rec_texts = overall_ocr.get("rec_texts", [])
            rec_boxes = overall_ocr.get("rec_boxes", [])
            rec_polys = overall_ocr.get("rec_polys", [])

            for idx, rec_text in enumerate(rec_texts):
                if not rec_text:
                    continue

                rec_text_normalized = normalize_text(rec_text)

                matched = False
                for keyword in keywords_normalized:
                    if keyword in rec_text_normalized:
                        matched = True
                        break

                if matched:
                    box = rec_boxes[idx] if idx < len(rec_boxes) else []
                    poly = rec_polys[idx] if idx < len(rec_polys) else []
                    matches.append({
                        "block_id": f"ocr_{idx}",
                        "block_content": rec_text,
                        "block_bbox": box if box else [],
                        "rec_poly": poly,
                        "layout_idx": layout_idx,
                        "match_type": "ocr"
                    })

    return matches


def find_field_positions(
        extract_info: Dict[str, str],
        json_result: Optional[Dict],
) -> Dict[str, List]:
    """
    找到提取的字段信息 在json中的位置信息
    """

    field_positions = {}  # 记录位置

    if json_result:
        for field_name, field_value in extract_info.items():
            if field_value and field_value != '-':
                # 搜索value的所有位置
                value_positions = find_text_positions_in_json(field_value, json_result)
                if value_positions:
                    # 如果有多个匹配，选择第一个
                    field_positions[field_name] = value_positions[:1]

    return field_positions
