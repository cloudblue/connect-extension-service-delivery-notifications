from datetime import datetime

import boto3
import markdown
import peewee
from fastapi import Depends
from cen import database, jinja
from cen.database import create_email_task, get_rule_product
from connect.eaas.core.inject.common import get_call_context, get_config

CHARSET = 'UTF-8'


def send_email(config, email_from, email_from_name, email_to, body, product_id):

    ses_client = boto3.client(
        'ses',
        aws_access_key_id=config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=config['AWS_SECRET_ACCESS_FOR_SES'],
        region_name=config['AWS_REGION'],
    )

    email_source = f'{email_from_name} <{email_from}>'
    email_to = email_to

    subject = f'New subscription for product {product_id}'

    response_email = ses_client.send_email(
        Destination={
            'ToAddresses': [
                email_to,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': body,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        },
        Source=email_source,
    )
    return response_email['ResponseMetadata']['RequestId']
