from openai import OpenAI
from openai.types.shared_params.response_format_text import ResponseFormatText


class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def create_prompt(self, query: str, context: str):
        """
        Create a prompt for the model to generate a relevant answer.
        """

        prompt = f"""
        Below are the most relevant pieces of information based on the given query. Please read them carefully and provide a concise, informative answer to the following question.

        Context:
        {context}

        Question:
        {query}

        Answer:
        """
        return prompt

    async def get_answer_to_question(self, query: str, context: str):
        """
        Generate an answer based on the query and relevant text chunks using GPT.
        """
        prompt = self.create_prompt(query, context)

        # Request completion from OpenAI
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Answer concisely and clearly to the given question.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format=ResponseFormatText(type="text"),
        )

        # Return the generated answer
        return completion.choices[0].message.content or None
