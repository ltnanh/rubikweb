import time
import asyncio
from fastapi import APIRouter, HTTPException

from core.config import MAX_CONCURRENT_SOLVES
from schemas.models import SolveRequest, SolveByFaceletRequest, SolveResponse
from services.solver_service import solve_cube_from_scramble, solve_cube_from_faceletstring

router = APIRouter()
solve_semaphore = asyncio.Semaphore(MAX_CONCURRENT_SOLVES)



@router.post("/api/solve", response_model=SolveResponse)
async def solve_rubik(request: SolveRequest):
    async with solve_semaphore:
        try:
            start = time.time()
            solution, p1_len, p2_len = await asyncio.to_thread(solve_cube_from_scramble, request.scramble)
            elapsed_ms = (time.time() - start) * 1000
            return SolveResponse(
                solution=solution,
                moves_count=len(solution),
                phase1_moves=p1_len,
                phase2_moves=p2_len,
                solving_time_ms=round(elapsed_ms, 2),
                success=True
            )
        except TimeoutError as e:
            raise HTTPException(status_code=408, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))




@router.post("/api/solve-by-facelet", response_model=SolveResponse)
async def solve_rubik_by_facelet(request: SolveByFaceletRequest):
    async with solve_semaphore:
        try:
            start = time.time()
            solution, p1_len, p2_len = await asyncio.to_thread(solve_cube_from_faceletstring, request.facelet_string)
            elapsed_ms = (time.time() - start) * 1000
            return SolveResponse(
                solution=solution,
                moves_count=len(solution),
                phase1_moves=p1_len,
                phase2_moves=p2_len,
                solving_time_ms=round(elapsed_ms, 2),
                success=True
            )
        except TimeoutError as e:
            raise HTTPException(status_code=408, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))



@router.get("/api/health")
async def health():
    return {"status": "ok"}
