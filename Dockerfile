FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod a+x startup.sh

EXPOSE 5000

ENTRYPOINT ["./startup.sh"]

