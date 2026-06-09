from typing import Dict, List, Any

headers_to_split_on = [
    ("#", "title"),
    ("##", "title"),
    ("###", "title"),
    ("####", "title"),
]


def split_markdown(content: str) -> Dict[str, Any]:
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    text_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on, strip_headers=False
    )
    docs = text_splitter.split_text(content)
    res_list = []
    dic = {}
    for idx, doc in enumerate(docs):
        text = doc.page_content
        title = doc.metadata["title"]
        dic["title"] = title
        dic["text"] = text
        dic["doc_id"] = f"doc_{idx}"
        res_list.append(dic)
    res = {"structure_json_result": res_list}
    return res
