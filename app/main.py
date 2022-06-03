from typing import List
from fastapi import FastAPI, UploadFile, Depends, Response, status

from . import crud, models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

# Создание таблиц в БД. Если они уже существуют,
# ничего не проиходит
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

MAX_NUMBER_OF_FILES = 15


def get_db():
    """
    Функция для получения сессии для работы с
    базой данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/frames/")
async def create_files(
    files: List[UploadFile], response: Response, db: Session = Depends(get_db)
):
    """
    Ручка для создания из файлов объектов в minio и записей о них в БД
    """
    # Обработка исключительных ситуаций
    expected_mime_type = "image/jpeg"
    if len(files) > MAX_NUMBER_OF_FILES or len(files) == 0:
        response.status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        return {"message": "Error : Too many or no files were upldoaded!"}
    for file in files:
        if file.content_type != expected_mime_type:
            response.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            return {"message": "Error : Wrong mime-type!"}
    # Работа с данными
    file_records = await crud.create_files_and_file_records(db=db, files=files)
    return file_records


@app.get("/frames/{request_code}")
def receive_files_by_request_code(
    request_code: int, response: Response, db: Session = Depends(get_db)
):
    """
    Ручка для получения записей о файлах с соответствующим значением кода
    """
    # Обработка исключительных ситуаций
    if request_code < 1 or request_code > MAX_NUMBER_OF_FILES:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "Error : Invalid code was used!"}
    # Работа с данными
    file_records = crud.get_file_records_by_code(db=db, code=request_code)
    return file_records


@app.delete("/frames/{request_code}")
def delete_files_by_request_code(
    request_code: int, response: Response, db: Session = Depends(get_db)
):
    """
    Ручка для удаления файлов из объектного хранилища и записей об
    этих файлах из БД, соответствующих данному коду
    """
    # Обработка исключительных ситуаций
    if request_code < 1 or request_code > MAX_NUMBER_OF_FILES:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"message": "Error : Invalid code was used!"}
    # Работа с данными
    deleted_files_number = crud.delete_files_and_file_records_by_code(
        db=db, code=request_code
    )
    return deleted_files_number
