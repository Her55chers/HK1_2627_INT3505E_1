# ─── stage 1: builder — cài thư viện vào venv ───
FROM python:3.12-slim AS builder
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── stage 2: runtime — chỉ copy venv + code ───
FROM python:3.12-slim
WORKDIR /app
RUN useradd -r -d /app app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=wsgi.py
USER app
EXPOSE 5000
# Tạo bảng rồi chạy Gunicorn (không dùng flask run trong production)
CMD ["sh", "-c", "flask init-db && gunicorn --bind 0.0.0.0:5000 --workers 2 wsgi:app"]
