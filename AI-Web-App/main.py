from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.llms import Ollama
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

db = None
llm = Ollama(model="phi")

@app.get("/")
def home():
    return {"message": "AI PDF Q&A running"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global db

    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_documents(chunks, embeddings)

    os.remove(file_path)

    return {"message": "PDF processed successfully"}

@app.get("/ask")
def ask(query: str):
    global db

    if db is None:
        return {"answer": "Upload PDF first"}

    docs = db.similarity_search(query, k=3)
    context = "\n".join([doc.page_content[:500] for doc in docs])

    prompt = f"""
    You are a thorough document analysis assistant.
    Answer the question based ONLY on the context below.
    Your answer must be detailed and comprehensive — a minimum of 5 sentences.
    For complex topics, provide more depth accordingly.
    If the answer is not found in the context, say "Not found in document."

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    response = llm.invoke(prompt)

    # ✅ response is a plain string with Ollama — no .content attribute
    return {"answer": response}