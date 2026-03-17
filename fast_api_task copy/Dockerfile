FROM python:3.11.8-slim-bookworm
RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev --no-install-recommends
COPY /requirements.txt /requirements.txt
RUN pip --no-cache-dir install -r /requirements.txt

WORKDIR /service
COPY /app /service/app
COPY /run.py /service/run.py
ENV APP_HOST=0.0.0.0
ENV APP_PORT=80
ENTRYPOINT ["python", "run.py"]
