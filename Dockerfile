# syntax=docker/dockerfile:1
# Python image: the container runs `python app.py` from /app (works with hosts that default to that start command).
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python build.py --local && useradd -r -u 10001 app && chown -R app /app
USER app
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=4s --start-period=10s --retries=3 \
  CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:%s/healthz'%os.environ.get('PORT','8080'),timeout=3)" || exit 1
CMD ["python", "app.py"]
