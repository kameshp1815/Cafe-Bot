
# src/routes/chat.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.schemas import ChatRequest
from services.chat_service  import ChatService
from utils.exceptions.custom_exceptions import BrewBaseException
from repositories.repo import ErrorLogRepository
router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat")
def post_chat(request: ChatRequest) -> JSONResponse:
    try:
        
        service = ChatService()
        reply   = service.handle_prompt(request)
        return JSONResponse(
            status_code = 200,
            content     = {
                "status" : "success",
                "data"   : {"reply": reply}
            }
        )

    except BrewBaseException as e:
        return JSONResponse(
            status_code = e.status_code,
            content     = e.to_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content     = {
                "status"     : "error",
                "error_code" : "BB_AGENT_001",
                "message"    : str(e)
            }
        )
