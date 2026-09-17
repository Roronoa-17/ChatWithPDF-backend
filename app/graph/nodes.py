from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from app.graph.state import GraphState
from app.services.vectorstore import get_vectorstore
from app.core.config import settings

llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL_NAME)
output_parser = StrOutputParser()

def retrieve_node(state: GraphState, config: RunnableConfig):
    # Extract the thread_id from LnagGraph's configuration
    active_namespace = config.get("configurable", {}).get("thread_id")
    print(f"DEBUG: Retriever is searching inside Namespace: {active_namespace}")
    if not active_namespace:
        raise ValueError("Critical Error: No thread_id provided to retriever!")
    # Passing namespace into vectorstore initialization
    vectorstore = get_vectorstore(namespace=active_namespace)
    
    # PDF specific chunks retrieval
    docs = vectorstore.similarity_search(state["question"], k=3)
    print(f"DEBUG: Retriever found {len(docs)} documents!")
    context = "\n\n".join([
        f"[Page {doc.metadata.get('page', 0) + 1}]: {doc.page_content}"
        for doc in docs
    ])
    return {"context": context, "sources": docs}

def generate_node(state: GraphState):
    prompt = (
        f"Answer the question using only the context.\n"
        f"Context: {state['context']}\n"
        f"Question: {state['question']}"
    )
    chain = llm | output_parser
    answer = chain.invoke(prompt)
    return {"answer": answer}