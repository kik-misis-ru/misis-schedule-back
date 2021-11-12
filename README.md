# МИР МИСиС - Backend

## Запуск приложения

1. Клонирование репозитория:
  > git clone https://github.com/kik-misis-ru/misis-schedule-back.git
2. Переходим в папку:
  > cd misis-hub
3. Добавляем заполняем .env реальными данными.
4. Создаем виртуальное окружение:
  > python virtualenv venv
4. Активируем виртуальное окружение.
  > venv\Scripts\activate
5. Устанавливаем модули из файла requirements.txt:
  > pip install -r requirements.txt
9. Запускаем сервер (--reload - опционально):
  >uvicorn main:app --reload 