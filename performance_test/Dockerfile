FROM python:3.11-slim

WORKDIR /performance_test

COPY ./ ./
RUN pip install -r ./requirements.txt
RUN  rm ./requirements.txt
WORKDIR /performance_test/app

CMD ["python", "main.py"]