
FROM public.ecr.aws/lambda/python:3.9


WORKDIR /var/task

COPY requirements.txt ./


RUN pip install -r requirements.txt


COPY . .


CMD ["main.lambda_handler"]