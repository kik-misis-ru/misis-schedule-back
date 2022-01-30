FROM python:3.9

# 
WORKDIR /code

# 
COPY ./mir-misis-back/requirements.txt /code/requirements.txt

# 
RUN pip install -r /code/requirements.txt

# 
COPY ./mir-misis-back /code

# 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]