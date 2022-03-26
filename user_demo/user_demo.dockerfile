FROM python:3.8
ENV PYTHONUNBUFFERED 1
WORKDIR /user_demo
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python3", "manage.py", "migrate"]
CMD ["python3", "manage.py", "runserver", "0:8000"]
ENV PYTHONPATH=/user_demo
EXPOSE 8000
