# yacor

## Описание
Это демонстрационная версия криптоаналитического инструмента. yacor - это
сервис для анализа безопасности криптографических примитивов блокчейна.

## Отказ от ответственности
Я настоятельно рекомендую использовать этот проект только в научных или
исследовательских целях.

## Референсная архитектура
```
                                            ┌───────────────────────────────┐
                                            │                               │
                                    ┌──────►│  ECDSA reused nonce attack    │
┌─────────┐                         │       │                               │
│         │                         │       └───────────────────────────────┘
│ Client  │◄──┬─ ── ── ── ── ── ── ─┤
│         │   │                     ├───┐   ┌───────────────────────────────┐
└─────────┘   │   ┌─────────────┐   │   │   │                               │
              │   │             │   │   └──►│  Other attack(s)              │
              └──►│   Backend   │◄──┘       │                               │
                  │             │           └───────────────────────────────┘
                  └─────────────┘
```
Проект yacor состоит из 3 основных модулей:
1. **Клиент (Client)**: простой клиент на Python, который сначала получает
информацию о доступных сервисах, а затем отправляет запросы на атаку к этим
сервисам.
2. **Бэкэнд (Backend)**: gRPC-сервер на Python, который предоставляет 2 API:
один для получения информации клиента, второй - для "подписки" сервисов атаки
на бэкэнд и предоставления их видимости клиенту. Как только сервис атаки
подписывается, бэкэнд начинает периодически выполнять проверку состояния для
обновления информации клиента. Бэкэнд также выступает в роли балансировщика
нагрузки между клиентом и несколькими сервисами атаки, реализующими одну и ту
же атаку.
3. **Сервис(ы) атаки (Attack service(s))**: gRPC-сервис на Python,
предоставляющий 2 сервиса: один для healthchecks, второй - для обработки
запросов пользователя. Как только сервис запущен, он сразу сообщает бэкэнду о
своем статусе обслуживания и начинает отвечать на сообщения healthcheck.

## Стэк технологий
Python, python-gRPC, google-protobuf

## Деплой

## Установка
1. Установите Python, docker-compose и Docker согласно инструкциям для вашей
системы. Затем выполните:
```sh
python -m venv env
source env/bin/activate
pip3 install --upgrade -r requirements.txt
```
чтобы установить все необходимые зависимости в только что созданное виртуальное
окружение Python.

2. Затем выполните `make all` для генерации всех объявлений protobuf.
```sh
make all
```

Для удаления сгенерированных определений proto, выполните `make clean`.

## Использование

### Запуск проекта локально через docker-compose
Лучший способ запустить этот проект без головной боли - использовать
docker-compose.
```sh
docker-compose up
```
Затем вы увидите логи периодических проверок состояния (healthcheck),
выполняемых службой бэкэнда.

Затем выполните
```sh
python client.py
```
чтобы подключиться к удаленной службе бэкэнда для получения всей информации о
работающих службах и выбрать атаку.

## Лицензия
Лицензия BSD 3-Clause. y4cer @ 2023.
