"""Tests module."""
import os
import shutil
from fastapi.testclient import TestClient
from fastapi import status
from PIL import Image


from ..main import app

client = TestClient(app)


def test_create_files_incorrect_number_of_entities():
    os.mkdir("test_assets")
    files = []

    # Создаем 16 файлов формата txt
    for index in range(16):
        filename = f"test_file_{index}.txt"
        with open(f"test_assets/{filename}", "w") as flow:
            flow.write("Hello, world!")
        files.append(
            ("files", (filename, open(f"test_assets/{filename}", "rb"), "text/plain"))
        )
    response = client.post("/frames/", files=files)

    # Удаляем временные сущности
    for file in files:
        file[1][1].close()
    shutil.rmtree("test_assets")

    assert response.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE


def test_create_files_mime_type():
    os.mkdir("test_assets")
    files = []

    # Создаем 2 файлов формата txt
    for index in range(2):
        filename = f"test_file_{index}.txt"
        with open(f"test_assets/{filename}", "w") as flow:
            flow.write("Hello, world!")
        files.append(
            ("files", (filename, open(f"test_assets/{filename}", "rb"), "text/plain"))
        )

    response = client.post("/frames/", files=files)

    # Удаляем временные сущности
    for file in files:
        file[1][1].close()
    shutil.rmtree("test_assets")

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_create_files():
    os.mkdir("test_assets")
    files = []
    width = height = 128
    solid_color_jpeg = Image.new(mode="RGB", size=(width, height), color="red")

    # Создаем 5 файлов формата jpg
    for index in range(5):
        filename = f"test_image_{index}.jpg"
        solid_color_jpeg.save(f"test_assets/{filename}")
        files.append(
            ("files", (filename, open(f"test_assets/{filename}", "rb"), "image/jpeg"))
        )
    response = client.post("/frames/", files=files)

    # Удаляем временные папки
    for file in files:
        file[1][1].close()
    shutil.rmtree("test_assets")

    assert response.status_code == status.HTTP_200_OK


def test_receive_files_by_request_code_incorrect_code():
    incorrect_codes = [-10, 0, 16]
    responses = []
    for incorrect_code in incorrect_codes:
        responses.append(client.get(f"/frames/{incorrect_code}"))
    for response in responses:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_receive_files_by_request_code():
    code = 7
    response = client.get(f"/frames/{code}")
    assert response.status_code == status.HTTP_200_OK


def test_delete_files_by_request_code_incorrect_code():
    incorrect_codes = [-10, 0, 16]
    responses = []
    for incorrect_code in incorrect_codes:
        responses.append(client.delete(f"/frames/{incorrect_code}"))
    for response in responses:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
