FROM python:3.9

WORKDIR /app
COPY gputracker-operator.py .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir kopf kubernetes

CMD ["kopf", "run", "gputracker-operator.py", "--verbose"]