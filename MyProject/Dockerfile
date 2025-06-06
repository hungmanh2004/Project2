FROM python:3.13.3

# Tạo thư mục làm việc
WORKDIR /code

# Copy project
COPY . .

# Cài pip và thư viện cần thiết
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Mở port 8000 cho WebSocket/API
EXPOSE 8000

# Chạy Daphne ASGI server (thay vì runserver)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "MyProject.asgi:application"]
