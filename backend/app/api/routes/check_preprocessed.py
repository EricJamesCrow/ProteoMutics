from fastapi import APIRouter
from pydantic import BaseModel

from app.data_handlers import Controller

class CheckPreprocessedFilesRequest(BaseModel):
    file_path: str
    type: str

router = APIRouter()

@router.post("/check")
async def check_preprocessed_files(request: CheckPreprocessedFilesRequest):
    file_path = request.file_path
    file_type = request.type
    is_preprocessed = Controller.check_if_pre_processed(file_path=file_path, typ=file_type)
    return {'is_preprocessed': is_preprocessed}