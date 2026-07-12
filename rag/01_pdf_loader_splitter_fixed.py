"""Clean PyPDFLoader + text splitter example.

Run:
    uv run python rag/01_pdf_loader_splitter_fixed.py

Why this exists:
    - Printing `loader` only shows the loader object.
    - Use `loader.load()` to get LangChain Document objects.
    - In current LangChain versions, import text splitters from
      `langchain_text_splitters`, not `langchain.text_splitter`.
"""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


PDF_PATH = Path(__file__).resolve().parent / "2412.19437v2.pdf"


def main() -> None:
    loader = PyPDFLoader(str(PDF_PATH))

    print("Loader object:")
    print(loader)
    print("\nThe line above is not an error. It only means the loader was created.")

    docs = loader.load()
    print("\nLoaded documents/pages:", len(docs))
    print("First page metadata:", docs[0].metadata)
    print("\nFirst 500 characters from page 1:")
    print(docs[0].page_content[:500])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(docs)

    print("\nCreated chunks:", len(chunks))
    print("First chunk metadata:", chunks[0].metadata)
    print("\nFirst 500 characters from chunk 1:")
    print(chunks[0].page_content[:500])


if __name__ == "__main__":
    main()
