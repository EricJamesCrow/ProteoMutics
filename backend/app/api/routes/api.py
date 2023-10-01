from fastapi import APIRouter

from app.api.routes import check_preprocessed, run_analysis, generate_graph, hello_world

router = APIRouter()
router.include_router(hello_world.router, tags=["Hello World"])
router.include_router(check_preprocessed.router, tags=["Check Preprocessed"])
router.include_router(run_analysis.router, tags=["Run Analysis"])
router.include_router(generate_graph.router, tags=["Generate Graph"])