FROM python:3.7

WORKDIR /app

COPY . .

RUN bash download_model.sh && pip install --no-cache-dir -r requirements.txt

# 服务运行的80端口
EXPOSE 80

CMD ["gunicorn", "app:app", "-c", "gunicorn.conf.py"]