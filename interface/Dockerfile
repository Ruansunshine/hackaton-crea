# Dockerfile para interface demo do Motor RAGFlow
FROM python:3.11-slim
WORKDIR /app
COPY app.py ./
COPY templates ./templates
RUN pip install flask requests
EXPOSE 8081
CMD ["python", "app.py"]
