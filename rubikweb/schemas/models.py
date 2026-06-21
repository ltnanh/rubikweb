from pydantic import BaseModel
from typing import List

class SolveRequest(BaseModel):
    scramble: str

class SolveByFaceletRequest(BaseModel):
    facelet_string: str

class SolveResponse(BaseModel):
    solution: List[str]
    moves_count: int
    phase1_moves: int
    phase2_moves: int
    solving_time_ms: float
    success: bool
