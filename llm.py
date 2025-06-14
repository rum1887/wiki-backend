from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=api_key,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an AI assistant that generates concise and meaningful tags for articles based on their summary and URL.",
        ),
        (
            "human",
    "Generate 2-3 tags that are broadly applicable across multiple articles based on the primary academic subject or university course the article would be relevant to.\n\n"
    "For example:\n"
    "- If the article discusses **nutrition**, it may align with a **Health & Wellness** course.\n"
    "- If it covers **protein synthesis**, it could be relevant to **Biochemistry** or **Molecular Biology**.\n"
    "- If it explores **AI in medicine**, it might fit under **Biomedical Engineering** or **Data Science**.\n\n"
    "**Summary:** {summary}\n"
    "**URL:** {url}\n\n"
    "Return a comma seperated list of strings"
        ),
    ]
)

chain = prompt | llm

def generate_tags(summary, url):
    response = chain.invoke({"summary": summary, "url": url})

    if hasattr(response, "content"):
        print(type(response.content))
        return response.content
    elif isinstance(response, str):  
        return response
    else:
        print("Unexpected response format:", response)
        return None

# print(generate_tags(
#     "Perplexity",
#     "Aravind Srinivas is the ceo and I'm an answer engine"
# ))