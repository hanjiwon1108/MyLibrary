FROM python:3.10.16
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y locales
RUN locale-gen ko_KR.UTF-8
# RUN apt-get install -y language-pack-ko
ENV LANG=ko_KR.UTF-8
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]  