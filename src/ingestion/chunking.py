from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(full_text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_text(full_text)

    print(f"\n📦 TOTAL CHUNKS CREATED: {len(chunks)}")

    return chunks