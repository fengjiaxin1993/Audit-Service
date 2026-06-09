from server.ocr_offline.ocr_extract_utils import _call_ocr_parse, process_file_ocr


def test_offline_parse():
    file_path = r"D:\github\Audit-Service\files\代理商-客户模板-产品 2025-B2-2491_青岛特锐德4500491759.pdf"
    result = _call_ocr_parse(file_path)
    if result:
        print("✅ 解析成功")
        print(result)
    else:
        print("❌ 解析失败")


def test_ocr_processor():
    file_path = r"D:\github\Audit-Service\data\files\代理商-客户模板-产品 2025-B2-2491_青岛特锐德4500491759.pdf"
    result = process_file_ocr(file_path)
    if result:
        print("✅ 解析成功")
        print(result)
    else:
        print("❌ 解析失败")


if __name__ == "__main__":
    # test_offline_parse()
    test_ocr_processor()
