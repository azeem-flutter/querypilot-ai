import time

from fastapi import APIRouter, Depends, Request

from app.core.config import Settings, get_settings
from app.llm.provider import get_provider
from app.schemas.requests import QueryRequest
from app.schemas.responses import QueryResponse
from app.services.query_service import QueryService

router = APIRouter(prefix="/api/v1")


def get_query_service(settings: Settings = Depends(get_settings)) -> QueryService:
    return QueryService(get_provider(settings))


@router.post("/query", response_model=QueryResponse)
async def submit_query(body: QueryRequest, request: Request,
                       service: QueryService = Depends(get_query_service)) -> QueryResponse:
    start = time.perf_counter()
    proposal = await service.propose(body.question)
    return QueryResponse(
        request_id=request.state.request_id,
        status=proposal.status,
        question=body.question,
        sql=proposal.sql,
        clarification_question=proposal.clarification_question,
        explanation=proposal.explanation,
        assumptions=proposal.assumptions,
        executed=False,
        duration_ms=int((time.perf_counter() - start) * 1000),
    )