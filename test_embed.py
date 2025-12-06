from app.embed import chunk_text, generate_embeddings, save_index

text = "This is a quick test. " * 200  # dummy text repeated

chunks = chunk_text(text, chunk_size=50)
print("chunks_count:", len(chunks))

embs = generate_embeddings(chunks)
print("embeddings_shape:", embs.shape)

save_index(embs, chunks, "testdoc")
print("saved: data/testdoc_embeddings.npy and data/testdoc_chunks.txt")
