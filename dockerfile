FROM python:3.11-rc-alpine

WORKDIR /code

RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["flask", "run", "--port=3000"]