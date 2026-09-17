from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.vectorstore import embeddings
from langchain_pinecone import PineconeVectorStore
from app.core.config import settings

def ingest_pdf(file_path: str, namespace: str) -> int:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    
    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        return 0
    
    print(f"DEBUG: Uploading {len(chunks)} chunks to Namespace: {namespace}")
    
    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=settings.PINECONE_INDEX_NAME,
        pinecone_api_key=settings.PINECONE_API_KEY,
        namespace=namespace # lock chunks to this specific ID
    )
    
    return len(chunks)