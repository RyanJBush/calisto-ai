from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.chat import QueryFilters
from app.services.hybrid_search_service import HybridSearchService
from app.services.retrieval_service import RetrievalFilters

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("/hybrid")
def hybrid_search(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    query = payload.get("query", "")
    top_k = int(payload.get("top_k", 8))
    filters = QueryFilters.model_validate(payload.get("filters") or {})
    retrieval_filters = RetrievalFilters(
        source_name=filters.source_name,
        document_ids=filters.document_ids,
        collection_id=filters.collection_id,
        section=filters.section,
        tags=filters.tags,
    )
    service = HybridSearchService(db)
    results = service.search(query=query, organization_id=user.organization_id, top_k=top_k, filters=retrieval_filters)
    return {
        "query": query,
        "results": [
            {
                "chunk_id": r.chunk.id,
                "document_id": r.chunk.document_id,
                "document_title": r.chunk.document.title,
                "snippet": r.chunk.content[:220],
                "semantic_score": round(r.semantic_score, 6),
                "bm25_score": round(r.bm25_score, 6),
                "rrf_score": round(r.score, 6),
            }
            for r in results
        ],
    }
