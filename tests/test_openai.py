# test_openai.py
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

resp = openai.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world"
)

print(resp.data[0].embedding[:10])  # prints first 10 numbers