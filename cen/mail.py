import boto3

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

CHARSET = 'UTF-8'


def send_email(
        config,
        email_from,
        email_from_name,
        email_to,
        body,
        product_id,
        subject=None,
):

    ses_client = boto3.client(
        'ses',
        aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS_SECRET_ACCESS_FOR_SES'],
        region_name=config['AWS_REGION'],
    )

    email_source = f'{email_from_name} <{email_from}>'

    if not subject:
        subject = f'New subscription for product {product_id}'

    msg = MIMEMultipart()
    msg.set_charset(CHARSET)
    msg.add_header('X-Environment', config.get('ENVIRONMENT', 'PRODUCTION'))
    msg['Subject'] = subject
    msg['From'] = email_source
    msg['To'] = email_to

    html_body = MIMEText(body, 'html')
    msg.attach(html_body)
    response_email = ses_client.send_raw_email(
        Source=email_source,
        Destinations=[email_to],
        RawMessage={
            'Data': msg.as_string().encode(CHARSET),
        },
    )
    return response_email['ResponseMetadata']['RequestId']
