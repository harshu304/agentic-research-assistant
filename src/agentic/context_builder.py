def build_context(chunks):

    context = ""

    for idx, chunk in enumerate(chunks, start=1):

        context += f"\n[CHUNK {idx}]\n"

        context += chunk[0]

        context += "\n"

    return context