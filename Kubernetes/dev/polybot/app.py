import flask
import os
import json
import boto3
from bot import ObjectDetectionBot
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

aws_region = os.environ.get('AWS_REGION', 'us-east-1')

client = boto3.session.Session().client(service_name='secretsmanager', region_name=aws_region)
cache_config = SecretCacheConfig()
cache = SecretCache(config=cache_config, client=client)

S3_PREDICTED_URL = os.getenv('S3_PREDICTED_URL')
if not S3_PREDICTED_URL:
    raise ValueError("The S3_PREDICTED_URL environment variable is not set.")

try:
    TELEGRAM_TOKEN_SECRET = cache.get_secret_string('davidhei-telegram-dev-token')
    TELEGRAM_TOKEN = json.loads(TELEGRAM_TOKEN_SECRET).get("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("The TELEGRAM_TOKEN could not be found in the secrets manager.")
except Exception as e:
    print(f"Error retrieving TELEGRAM_TOKEN from Secrets Manager: {str(e)}")
    raise

TELEGRAM_APP_URL = os.environ.get('TELEGRAM_APP_URL')
if not TELEGRAM_APP_URL:
    raise ValueError("The TELEGRAM_APP_URL environment variable is not set.")

dynamodb = boto3.resource('dynamodb', region_name=aws_region)
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
if not table_name:
    raise ValueError("The DYNAMODB_TABLE_NAME environment variable is not set.")
table = dynamodb.Table(table_name)

sqs_client = boto3.client('sqs', region_name=aws_region)
sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
if not sqs_queue_url:
    raise ValueError("The SQS_QUEUE_URL environment variable is not set.")

app = flask.Flask(__name__)

# Initialize the bot at the module level
try:
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL, sqs_queue_url, aws_region)
except Exception as e:
    print(f"Error initializing bot: {str(e)}")
    raise

# Flask routes
@app.route('/', methods=['GET'])
def index():
    return 'Ok'

@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    try:
        req = flask.request.get_json()
        bot.handle_message(req['message'])
        return 'Ok'
    except Exception as e:
        print(f"Error handling webhook request: {str(e)}")
        return 'Error', 500

@app.route('/results', methods=['POST'])
def results():
    try:
        prediction_id = flask.request.args.get('predictionId')
        if not prediction_id:
            prediction_id = flask.request.json.get('predictionId')

        if not prediction_id:
            return 'predictionId is required', 400

        response = table.get_item(Key={'prediction_id': prediction_id})

        if 'Item' in response:
            item = response['Item']
            chat_id = item['chat_id']
            labels = item['labels']

            text_results = f"Prediction results for image {item['original_img_path']}:\n"
            for label in labels:
                text_results += f"- {label['class']} at ({label['cx']:.2f}, {label['cy']:.2f}) with size ({label['width']:.2f}, {label['height']:.2f})\n"

            bot.send_text(chat_id, text_results)

            file_name = os.path.basename(item['original_img_path'])
            s3_full_url = f"{S3_PREDICTED_URL}{file_name}"

            bot.send_text(chat_id, "You can download the predicted image here:")
            bot.send_text(chat_id, s3_full_url)
            return 'Ok'
        else:
            return 'No results found', 404
    except Exception as e:
        print(f"Error processing results: {str(e)}")
        return 'Error', 500


@app.route('/loadTest/', methods=['POST'])
def load_test():
    try:
        req = flask.request.get_json()
        bot.handle_message(req['message'])
        return 'Ok'
    except Exception as e:
        print(f"Error handling load test: {str(e)}")
        return 'Error', 500

if __name__ == "__main__":
    try:
        # Check if running locally or in production
        if os.getenv('ENV') == 'production':
            ssl_cert_path = os.getenv('SSL_CERT_PATH', '/etc/ssl/certs/certificate.pem')
            ssl_key_path = os.getenv('SSL_KEY_PATH', '/etc/ssl/private/private.key')
        else:
            ssl_cert_path = os.getenv('SSL_CERT_PATH', '/home/ubuntu/YOURPUBLIC.pem')
            ssl_key_path = os.getenv('SSL_KEY_PATH', '/home/ubuntu/YOURPRIVATE.key')

        app.run(host='0.0.0.0', port=8443, ssl_context=(ssl_cert_path, ssl_key_path))
    except Exception as e:
        print(f"Error starting Flask application: {str(e)}")
        raise
