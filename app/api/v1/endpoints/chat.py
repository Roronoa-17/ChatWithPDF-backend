from fastapi import APIRouter
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.schemas.chat import ChatRequest, ChatResponse
from app.graph.workflow import workflow
from app.core.database import pool
import json
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/chat") 
async def chat_endpoints(request: ChatRequest):
    saver = AsyncPostgresSaver(pool)
    app_graph = workflow.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": request.thread_id}}
    
    
    async def event_stream():
        # using astream_events to intercept real-time LLM outputs
        async for event in app_graph.astream_events(
            {"question": request.question},
            config=config,
            version="v2"
        ):
            kind = event["event"]
            # model's streaming tokens
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content

                # normalizing chunk to string
                text_to_send = ""
                if isinstance(chunk, str):
                    text_to_send = chunk
                elif isinstance(chunk, list):
                    # in case gemini outputs structured blocks
                    for part in chunk:
                        if isinstance(part, dict):
                            text_to_send += part.get("text", "")
                        elif isinstance(part, str):
                            text_to_send += part
                elif isinstance(chunk, dict):
                    text_to_send = chunk.get("text", "")
                
                if text_to_send:
                    yield f"data: {json.dumps({'text': text_to_send})}\n\n"
        # informing frontend that the generation is complete
        yield "data: [DONE]\n\n"
        
    # returning the stream
    return StreamingResponse(event_stream(), media_type="text/event-stream")
