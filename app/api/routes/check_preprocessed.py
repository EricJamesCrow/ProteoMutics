from app.data_handlers import controller

def check_preprocessed_files(file_path: str, file_type: str) -> bool:
    file_path = file_path
    file_type = file_type
    is_preprocessed = controller.check_if_pre_processed(file_path=file_path, typ=file_type)
    return {'is_preprocessed': is_preprocessed}