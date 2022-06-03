from sqlalchemy.orm import Session, defer
from datetime import datetime
from typing import List
from . import models, schemas
from uuid import uuid1

from .object_storage import minioClient

from fastapi import UploadFile


async def create_files_and_file_records(db: Session, files: List[UploadFile]):
    mime_type = "image/jpeg"
    # Автоматически генерируемый код запроса для каждого файла в хранилище
    # определим как количество сущностей в запросе, в рамках которого
    # данный файл попал в хранилище.
    code = len(files)
    current_bucket = datetime.today().strftime("%Y%m%d")
    found = minioClient.bucket_exists(current_bucket)
    if not found:
        minioClient.make_bucket(current_bucket)

    db_file_records = []
    file_records = []
    for file in files:
        # Поскольку sdk minio нельзя передать корутину, пользуемся
        # синхронным интерфейсом файла через .file
        sync_file = file.file
        file_size = len(sync_file.read())
        filename = str(code) + "-" + str(uuid1()) + ".jpg"

        registration_datetime = datetime.now()
        db_file_records.append(
            models.FileRecord(
                code=code,
                filename=filename,
                bucket=current_bucket,
                registration_datetime=registration_datetime,
            )
        )
        file_records.append(
            schemas.FileRecord(
                code=code,
                filename=filename,
                registration_datetime=registration_datetime.strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
            )
        )

        sync_file.seek(0)

        minioClient.put_object(
            current_bucket, filename, sync_file, file_size, content_type=mime_type,
        )
        await file.close()

    db.bulk_save_objects(db_file_records)
    db.commit()
    return file_records


def get_file_records_by_code(db: Session, code: int):
    db_files_records_with_certain_code = (
        db.query(models.FileRecord)
        .options(defer("code"))
        .filter(models.FileRecord.code == code)
    ).all()
    files_records_with_certain_code = [
        schemas.FileRecord(
            code=db_file_record_with_certain_code.code,
            filename=db_file_record_with_certain_code.filename,
            registration_datetime=db_file_record_with_certain_code.registration_datetime.strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
        )
        for db_file_record_with_certain_code in db_files_records_with_certain_code
    ]
    return files_records_with_certain_code


def delete_files_and_file_records_by_code(db: Session, code: int):
    code = str(code)
    buckets = minioClient.list_buckets()
    file_records_for_deletion = db.query(models.FileRecord).filter(
        models.FileRecord.code == code
    )
    for bucket_name in map(lambda bucket: bucket.name, buckets):
        bucket_files_for_deletion = filter(
            lambda file: file.bucket == bucket_name, file_records_for_deletion
        )

        for filename in map(lambda file: file.filename, bucket_files_for_deletion):
            minioClient.remove_object(bucket_name, filename)

    deleted_file_records_number = file_records_for_deletion.delete()
    db.commit()
    return deleted_file_records_number

