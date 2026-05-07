from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/e5-small-v2")
import torch
torch.set_num_threads(6) 
def embed_batch(texts):
    # 🔥 IMPORTANT: use "passage:" prefix
    texts = ["passage: " + t for t in texts]

    return model.encode(
        texts,
        batch_size=64,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True
    ).tolist()


def embed_query(query):
    return model.encode(
        "query: " + query,   # 🔥 IMPORTANT
        normalize_embeddings=True
    ).tolist()