import os
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Load the knowledge base
with open("medical_knowledge.json", "r") as file:
    knowledge_base = json.load(file)

# Request Model
class Query(BaseModel):
    question: str

def search_knowledge_base(query: str):
    """Check if a term exists in the knowledge base and return the answer if found."""
    query_lower = query.lower()
    for key in knowledge_base:
        if key in query_lower:
            return knowledge_base[key]
    return None

def get_pubmed_citation(query: str):
    """Fetch a relevant citation from PubMed."""
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        article_ids = data.get("esearchresult", {}).get("idlist", [])
        if article_ids:
            return f"https://pubmed.ncbi.nlm.nih.gov/{article_ids[0]}"
    return None

@app.post("/ask")
def ask_chatbot(query: Query):
    """Handles user queries and fetches AI-generated responses."""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a medical AI assistant."},
                      {"role": "user", "content": query.question}]
        )

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Medical AI Chatbot API is running!"}
