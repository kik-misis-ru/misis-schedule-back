# МИР МИСиС - Backend

## Запуск приложения

1. Клонирование репозитория:
  > git clone https://github.com/kik-misis-ru/misis-schedule-back.git
2. Создаём папку:
  > mkdir misis-back
2. Переходим в папку:
  > cd misis-back
3. Добавляем заполняем .env реальными данными.
4. Создаем виртуальное окружение:
  > python virtualenv venv
5. Активируем виртуальное окружение.
  > venv\Scripts\activate
6. Устанавливаем модули из файла requirements.txt:
  > pip install -r requirements.txt
7. Запускаем сервер (--reload - опционально):
  >uvicorn main:app --reload 