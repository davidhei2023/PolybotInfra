FROM python:3.10-alpine
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV TELEGRAM_APP_URL="https://davidhei-polybot-k8s.int-devops.click"
ENV DYNAMODB_TABLE_NAME="davidhei-k8s-dev-bot-dynamo-table"
ENV POLYBOT_RESULTS_URL="davidhei-polybot-k8s.int-devops.click"
ENV SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/019273956931/davidhei-k8s-dev-bot-sqs"
ENV S3_BUCKET_NAME="davidhei-k8s-dev-s3-bucket"
ENV AWS_REGION="us-east-1"
ENV POLYBOT_RESULTS_URL="https://davidhei-polybot-k8s.int-devops.click/results"
ENV S3_PREDICTED_URL="https://davidhei-k8s-dev-s3-bucket.s3.amazonaws.com/predicted/"

EXPOSE 8443

COPY . .

CMD ["python", "app.py"]