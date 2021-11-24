# МИР МИСиС - бэкенд - misis-schedule-back

Репозиторий содержит исходный код серверной части приложения "Мир МИСиС".

Приложение "Мир МИСиС" предназначено для просмотра расписания и получения другой информации о "НИТУ МИСиС".
                       
Более подробную информацию о приложении см. https://github.com/kik-misis-ru/misis-schedule-front.git


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
