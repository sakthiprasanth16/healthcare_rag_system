from pinecone import Pinecone
from backend.config import config


class VectorStore:
    def __init__(self):
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self.index = pc.Index(config.PINECONE_INDEX_NAME)

    def upsert_chunks(self, chunks: list, user_id: str) -> tuple[int, list]:
        """
        Upsert embedded chunks to Pinecone under the given namespace (user_id = session_id).
        Returns (chunk_count, vector_ids).
        """
        vectors = []
        vector_ids = []

        for chunk in chunks:
            vec_id = chunk["id"]
            vector_ids.append(vec_id)
            vectors.append({
                "id": vec_id,
                "values": chunk["embedding"],
                "metadata": {
                    "text": chunk["text"],
                    "file_name": chunk["file_name"],
                    "chunk_index": chunk["chunk_index"]
                }
            })

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch, namespace=user_id)

        return len(vectors), vector_ids

    def search(self, query_embedding: list, user_id: str, top_k: int = 5) -> list:
        """
        Search Pinecone for similar chunks in the given namespace.
        Returns list of chunk dicts with text, file_name, chunk_index, score.
        """
        result = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=user_id,
            include_metadata=True
        )

        chunks = []
        for match in result.get("matches", []):
            metadata = match.get("metadata", {})
            chunks.append({
                "text": metadata.get("text", ""),
                "file_name": metadata.get("file_name", "unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "score": match.get("score", 0.0)
            })

        return chunks

    def delete_vectors(self, vector_ids: list, namespace: str):
        """Permanently delete vectors from Pinecone by their IDs."""
        # Delete in batches of 100
        batch_size = 100
        for i in range(0, len(vector_ids), batch_size):
            batch = vector_ids[i:i + batch_size]
            self.index.delete(ids=batch, namespace=namespace)
