FROM python:3.7

WORKDIR /app

COPY . .

RUN bash download_model.sh && pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]