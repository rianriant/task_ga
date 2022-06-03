# Тестовое задание для компании Гринатом

1. Заполните `.env` согласно `example.env`
2. Выполните команду `docker-compose up`
3. Необходимо создать сервисный аккаунт через графический интерфейс minio (Identity -> Service accounts -> Create service accounts) с указанными в `.env` `access key` и `secret key`.
4. Для тестирования нужно зайти в контейнер с приложением :
   `docker exec -it {python app container's name} /bin/bash`
   И изнутри контейнера запустить тесты :
   `pytest --pyargs app`

_Соискатель Григорян Владислав_
_@vladgrigorian_
