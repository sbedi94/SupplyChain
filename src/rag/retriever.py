from langchain_core.documents import Document

def get_supplier_context() -> str:
    docs = [
        Document(page_content="Category X supplier lead time is 6 weeks."),
        Document(page_content="Alternate suppliers exist in Category X."),
        Document(page_content="Black Friday requires 3x safety stock."),
        Document(page_content="Finance approval required if budget exceeded.")
    ]

    return "\n".join(d.page_content for d in docs)
