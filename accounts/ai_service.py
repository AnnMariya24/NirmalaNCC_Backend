
# 1. SETUP - Get your key from https://console.groq.com/
# client = Groq(api_key="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")
import os
from groq import Groq # type: ignore
from .models import NCCHandbook
from django.db.models import Q

# It is highly recommended to use an environment variable for the key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
#client = Groq(api_key="") # Use the full gsk_ key

class NCCAIHandler:
    @staticmethod
    def ask_ai(user_query):
        # 1. Search for context
        keywords = user_query.split()[:3]
        query_filter = Q()
        for word in keywords:
            if len(word) > 3:
                query_filter |= Q(content_text__icontains=word)

        relevant_books = NCCHandbook.objects.filter(query_filter).exclude(content_text__isnull=True)[:2]
        
        # Fallback: If no keywords match, just get the latest handbook text
        if not relevant_books.exists():
            relevant_books = NCCHandbook.objects.exclude(content_text__isnull=True).order_by('-uploaded_at')[:1]

        knowledge_base = ""
        for book in relevant_books:
            knowledge_base += f"\n[SOURCE: {book.title}]\n{book.content_text[:5000]}"

        # 2. Call Groq
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are 'Auralis', an NCC expert assistant. Use the Knowledge Base to answer the cadet's questions precisely."
                    },
                    {
                        "role": "user",
                        "content": f"KNOWLEDGE BASE:\n{knowledge_base}\n\nQUESTION: {user_query}"
                    }
                ],
                model="llama-3.3-70b-versatile", # Using the smarter model
                temperature=0.3,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error connecting to Groq: {str(e)}"