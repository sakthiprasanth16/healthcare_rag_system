import google.generativeai as genai
from backend.config import config
from backend.prompts.healthcare_prompt import build_prompt


class LLMService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.LLM_MODEL)

    def generate_answer(self, question: str, context_chunks: list, chat_history: list) -> dict:
        """
        Generate a RAG answer given retrieved context chunks and chat history.

        Returns:
            {
                "answer": str,
                "sources": [{"file_name": str, "chunk_index": int}, ...]
            }
        """
        # Build context string from chunks
        if not context_chunks:
            context_str = "No relevant context found in the uploaded documents."
        else:
            context_parts = []
            for i, chunk in enumerate(context_chunks):
                context_parts.append(
                    f"[Chunk {i+1} | File: {chunk['file_name']} | Section: {chunk['chunk_index']}]\n"
                    f"{chunk['text']}"
                )
            context_str = "\n\n---\n\n".join(context_parts)

        # Build history string (last 6 messages)
        recent_history = chat_history[-6:] if len(chat_history) > 6 else chat_history
        history_parts = []
        for msg in recent_history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            history_parts.append(f"{role}: {msg.get('content', '')}")
        history_str = "\n".join(history_parts) if history_parts else "No prior conversation."

        # Build prompt
        prompt = build_prompt(
            context=context_str,
            history=history_str,
            question=question
        )

        # Generate answer
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=1500,
                )
            )
            answer_text = response.text.strip()
        except Exception as e:
            answer_text = f"⚠️ Error generating response: {str(e)}"

        # Build sources list (deduplicated by file + chunk)
        seen = set()
        sources = []
        for chunk in context_chunks:
            key = (chunk["file_name"], chunk.get("chunk_index", 0))
            if key not in seen:
                seen.add(key)
                sources.append({
                    "file_name": chunk["file_name"],
                    "chunk_index": chunk.get("chunk_index", 0)
                })

        return {
            "answer": answer_text,
            "sources": sources
        }
