from pinecone import Pinecone, ServerlessSpec
import openai

from src.types.pipecode_data_types import QueryResult, TextData
from src.utils.config import OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY


# Pinecone Client Class
class PineconeClient:
    def __init__(self, api_key: str, index_name: str, embedding_dim: int = 1536):
        self.api_key = api_key
        self.index_name = index_name
        self.embedding_dim = embedding_dim

        pc = Pinecone(api_key=api_key)
        self.pinecone_client = pc
        # Initialize Pinecone
        # Now do stuff
        if index_name not in pc.list_indexes().names():
            self.index = pc.create_index(
                name=self.index_name,
                dimension=self.embedding_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        self.index = pc.Index(index_name)

    async def get_embedding(self, text: str) -> list[float]:
        res = openai.embeddings.create(
            input=[text], model="text-embedding-3-small", dimensions=self.embedding_dim
        )

        text_embeddings = [e.embedding for e in res.data]

        return text_embeddings[0]

    async def upsert_vectors(self, text_data: list[TextData]):
        vectors_to_upsert = []

        for item in text_data:
            # Get the embedding for the text
            embedding = await self.get_embedding(item.text)

            # Prepare the metadata to include the original text
            metadata = {"text": item.text}  # Add the original text as metadata

            # Append the vector as a dictionary with the necessary data
            vectors_to_upsert.append(
                {"id": item.id, "values": embedding, "metadata": metadata}
            )

        # Upsert vectors into Pinecone
        self.index.upsert(vectors=vectors_to_upsert)

    async def query(self, query_text: str, top_k: int = 5) -> QueryResult | None:

        # Generate embedding for the query text
        query_embedding = await self.get_embedding(query_text)

        # Query Pinecone for similar vectors
        query_result = self.index.query(
            vector=query_embedding, top_k=top_k, include_metadata=True
        )

        matched_chunks = query_result["matches"]

        if not matched_chunks:
            return None

        # Return the highest score match as a QueryResult object
        return [
            QueryResult(
                id=chunck["id"],
                score=chunck["score"],
                text=chunck["metadata"]["text"],
            )
            for chunck in matched_chunks
        ]
