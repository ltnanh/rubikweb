import sys
import os
import time
import multiprocessing

# Thêm kociemba vào sys.path để có thể import
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "kociemba"))

from RubikCUbeFacelet import FaceletCube
from solve import solve_cube
from core.config import SOLVE_TIMEOUT_SECONDS

def _solve_cube_from_scramble_stream(scramble_str: str):
    fc = FaceletCube()
    fc.scramble(scramble_str)
    initial_cube = fc.to_rubik_cube()
    for solution, p1_len, p2_len in solve_cube(initial_cube, timeout=SOLVE_TIMEOUT_SECONDS):
        yield solution, p1_len, p2_len

def _solve_cube_from_faceletstring_stream(facelet_string: str):
    fc = FaceletCube(facelet_string)
    initial_cube = fc.to_rubik_cube()
    for solution, p1_len, p2_len in solve_cube(initial_cube, timeout=SOLVE_TIMEOUT_SECONDS):
        yield solution, p1_len, p2_len

def _solve_worker(mode: str, payload: str, conn):
    try:
        if mode == "scramble":
            solution_stream = _solve_cube_from_scramble_stream(payload)
        elif mode == "facelet":
            solution_stream = _solve_cube_from_faceletstring_stream(payload)
        else:
            raise ValueError(f"Unknown solve mode: {mode}")

        found_solution = False
        for solution, p1_len, p2_len in solution_stream:
            found_solution = True
            conn.send(("solution", (solution, p1_len, p2_len)))

        if not found_solution:
            raise ValueError("Can't find solution")

        conn.send(("done", None))
    except Exception as e:
        conn.send(("error", str(e)))
    finally:
        conn.close()

def _get_multiprocessing_context():
    try:
        return multiprocessing.get_context("fork")
    except ValueError:
        return multiprocessing.get_context()

def _solve_with_hard_timeout(mode: str, payload: str, timeout: float):
    ctx = _get_multiprocessing_context()
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    process = ctx.Process(target=_solve_worker, args=(mode, payload, child_conn))

    start = time.monotonic()
    deadline = start + timeout
    last_solution = None
    last_error = None

    process.start()
    child_conn.close()

    try:
        while True:
            while parent_conn.poll():
                status, data = parent_conn.recv()
                if status == "solution":
                    last_solution = data
                elif status == "done":
                    process.join(timeout=0.2)
                    if last_solution is None:
                        raise ValueError("Can't find solution")
                    return last_solution
                elif status == "error":
                    last_error = data

            if last_error is not None:
                raise ValueError(last_error)

            if not process.is_alive():
                process.join(timeout=0.2)
                if last_solution is not None:
                    return last_solution
                raise ValueError("Can't find solution")

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1.0)

                if last_solution is not None:
                    return last_solution
                raise TimeoutError(f"Solving exceeded {timeout}s")

            parent_conn.poll(min(0.05, remaining))
    finally:
        parent_conn.close()

def solve_cube_from_scramble(scramble_str: str):
    return _solve_with_hard_timeout("scramble", scramble_str, SOLVE_TIMEOUT_SECONDS)

def solve_cube_from_faceletstring(facelet_string: str):
    return _solve_with_hard_timeout("facelet", facelet_string, SOLVE_TIMEOUT_SECONDS)
