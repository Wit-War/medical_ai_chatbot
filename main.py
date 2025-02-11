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

# Store chat history in memory
chat_history = {}

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

def log_chat(user_query, ai_response):
    """Logs user queries and AI responses."""
    with open("logs.txt", "a") as log_file:
        log_file.write(f"User: {user_query}\nAI: {ai_response}\n\n")

@app.post("/ask")
def ask_chatbot(query: Query):
    """Handles user queries, provides structured responses, remembers chat history, and logs queries."""
    try:
        user_id = "default_user"  # Change this when implementing user authentication

        # Initialize conversation history if not present
        if user_id not in chat_history:
            chat_history[user_id] = []

        # Add user message to chat history
        chat_history[user_id].append({"role": "user", "content": query.question})

        # Check knowledge base first
        knowledge_response = search_knowledge_base(query.question)
        if knowledge_response:
            return {"response": knowledge_response, "source": "Knowledge Base"}

        # Query OpenAI with chat history
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a medical AI assistant. Format responses into sections: Definition, Symptoms, Causes, Treatment, and Sources. Remember previous messages for follow-up questions."}
            ] + chat_history[user_id]
        )

        # Extract response text
        answer = response.choices[0].message.content
        
        # Add AI response to chat history
        chat_history[user_id].append({"role": "assistant", "content": answer})

        # Fetch PubMed citation
        citation = get_pubmed_citation(query.question)
        
        # Log the conversation
        log_chat(query.question, answer)

        return {
            "response": answer,
            "source": "AI Model",
            "citation": citation if citation else "No citation found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
