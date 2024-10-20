import os
import time
import telebot
import boto3
import json
from loguru import logger
from botocore.exceptions import NoCredentialsError
from telebot.types import InputFile

class Bot:
    def __init__(self, token, telegram_chat_url):
        self.telegram_bot_client = telebot.TeleBot(token)

        # Check current webhook
        current_webhook = self.telegram_bot_client.get_webhook_info()
        webhook_url = f'{telegram_chat_url}/{token}/'

        if current_webhook.url != webhook_url:
            self.telegram_bot_client.remove_webhook()
            time.sleep(0.5)

            if os.getenv('ENV') == 'production':
                # In production, do not pass the certificate
                self.telegram_bot_client.set_webhook(url=webhook_url, timeout=60)
            else:
                # In local mode, use a self-signed cert
                cert_path = os.getenv('SSL_CERT_PATH', '/home/ubuntu/YOURPUBLIC.pem')
                if not os.path.exists(cert_path):
                    raise FileNotFoundError(f"Certificate file not found at {cert_path}")
                with open(cert_path, 'rb') as cert_file:
                    self.telegram_bot_client.set_webhook(url=webhook_url, timeout=60, certificate=cert_file)

            logger.info('Webhook set successfully')
        else:
            logger.info('Webhook is already set')

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    # Define the missing methods
    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        file_id = msg['photo'][-1]['file_id']
        file_info = self.telegram_bot_client.get_file(file_id)
        downloaded_file = self.telegram_bot_client.download_file(file_info.file_path)
        file_path = f"/tmp/{file_id}.jpg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        return file_path

    def upload_to_s3(self, file_path, bucket_name, s3_file_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.upload_file(file_path, bucket_name, s3_file_name)
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
            return s3_url
        except NoCredentialsError:
            logger.error("Credentials not available for S3 upload")
            return None

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

class ObjectDetectionBot(Bot):
    def __init__(self, token, telegram_chat_url, sqs_queue_url, aws_region):
        super().__init__(token, telegram_chat_url)
        self.sqs_client = boto3.client('sqs', region_name=aws_region)
        self.sqs_queue_url = sqs_queue_url

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            try:
                photo_path = self.download_user_photo(msg)
                logger.info(f"Photo downloaded to: {photo_path}")

                s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
                if not s3_bucket_name:
                    raise ValueError("S3_BUCKET_NAME environment variable is not set.")
                s3_file_name = os.path.basename(photo_path)
                s3_url = self.upload_to_s3(photo_path, s3_bucket_name, s3_file_name)

                if not s3_url:
                    self.send_text(msg['chat']['id'], "Failed to upload image to S3.")
                    return

                logger.info(f"Photo uploaded to S3: {s3_url}")

                # Send a job to SQS
                job_message = {
                    'img_name': s3_file_name,
                    'chat_id': msg['chat']['id']
                }

                self.sqs_client.send_message(QueueUrl=self.sqs_queue_url, MessageBody=json.dumps(job_message))
                self.send_text(msg['chat']['id'], "Your image has been received and is being processed.")

            except Exception as e:
                logger.error(f"Error in handling message: {str(e)}")
                self.send_text(msg['chat']['id'], "An error occurred while processing your image.")
        else:
            self.send_text(msg['chat']['id'], "Please send a photo for object detection.")
