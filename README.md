![foodgram](https://github.com/ainokyn/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# «Продуктовый помощник»

Дипломный проект курса Python-разработчик на Яндекс.Практикум.

## Описание проекта Продуктовый помощник
На этом сервисе пользователи смогут публиковать рецепты, подписываться
на публикации других пользователей, добавлять понравившиеся рецепты в список 
«Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых 
для приготовления одного или нескольких выбранных блюд.

## Стек технологий

- Python 3
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Установка и запуск docker

**Подготовка ОС Windows**

Нативная ОС для Docker — Linux, поэтому запуск Docker-контейнеров на
Windows должен происходить внутри виртуальной машины с ОС Linux. 
Для этого нужно настроить систему виртуализации. Для разных версий Windows доступны
разные системы виртуализации.

**Установка Docker на Windows 10/11 и MacOS**

Зайдите на официальный сайт проекта https://www.docker.com/products/docker-desktop
и скачайте установочный файл Docker Desktop для вашей операционной системы.
Запустите его и следуйте инструкциям по установке. 

**Windows 10: Корпоративная и Pro**

Для Корпоративной и Pro-версий Windows виртуализация настраивается на основе гипервизора Hyper-V.

**Windows 10 Home**

Для корректной работы Docker в Windows 10 Home установите подсистему Linux (WSL2) по инструкции с официального сайта Microsoft.

**Windows 7**

Для настройки системы виртуализации в Windows 7:
- скачайте и установите специальную программу для работы с виртуальными машинами, например, VMWare или VirtualBox;
- скачайте образ Ubuntu;
- установите Docker по инструкции для Linux.

**Установка Docker на Linux**

1. Установка утилиты для скачивания файлов
```
sudo apt install curl
```
3. Эта команда скачает скрипт для установки докера
```
curl -fsSL https://get.docker.com -o get-docker.sh
```
4. Эта команда запустит его
```
sh get-docker.sh
```
6. В терминале надо удалить старые версии командой:
```
sudo apt remove docker docker-engine docker.io containerd runc
```
8. Обновить список для менеджера пакетов ATP:
```
sudo apt update 
```
10. Установить пакеты для работы через протокол https:
```
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y
  ```
7. Добавить ключ GPG для подтверждения подлинности в процессе установки:
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
9. Добавить репозиторий Docker в пакеты apt:
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" 
```
10. Обновление индексов процессов:
```
sudo apt update 
```

## Запуск проекта

1. Заполнить .env файл для своего проекта в соответствии с шаблоном
***
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
***
DB_NAME=postgres # имя базы данных
***
POSTGRES_USER=postgres # логин для подключения к базе данных
***
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
***
DB_HOST=db # название сервиса (контейнера)
***
DB_PORT=5432 # порт для подключения к БД 

2. Запускаем контейнеры
```
docker-compose up -d --build
```
3. Выполняем миграции
```
docker-compose exec web python manage.py migrate
```
4. Создаем суперюзера
```
docker-compose exec web python manage.py createsuperuser
```
5. Собираем статику
```
docker-compose exec web python manage.py collectstatic --no-input
```
6. При необходимости останавливаем котейнеры
```
docker-compose down -v 
``` 

