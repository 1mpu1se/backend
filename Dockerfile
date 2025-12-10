# Stage 1 - Build
FROM    python:3.12-slim AS build

WORKDIR /app

COPY    ./requirements.txt ./

RUN     pip install --no-cache-dir -r ./requirements.txt

# Stage 2 - Production
FROM    python:3.12-slim

WORKDIR /app

COPY    --from=build /usr/local/bin/ /usr/local/bin/
COPY    --from=build /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

COPY    ./src ./

ENV     PYTHONUNBUFFERED=1
ENV     PYTHONDONTWRITEBYTECODE=1

CMD     ["python", "main.py"]

EXPOSE  8080/tcp
