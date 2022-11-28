import os

from cen import mail


def test_send_email(
    mocker,
):
    config = {
        'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL'),
        'AWS_ACCESS_KEY_ID': 'access_id',
        'AWS_SECRET_ACCESS_FOR_SES': 'access_secret',
        'AWS_REGION': 'region',
    }
    test_email = 'test@receiver.com'
    test_name = 'test_name'
    test_sender = 'test@sender.com'
    body = '<p>rendered body</p>'
    subject = 'New subscription for product PRD-000'
    product_id = 'PRD-000'

    mocked_ses_client = mocker.MagicMock()
    mocked_boto3 = mocker.patch('cen.mail.boto3.client', return_value=mocked_ses_client)
    CHARSET = 'UTF-8'
    mail.send_email(config, test_sender, test_name, test_email, body, product_id)
    mocked_ses_client.send_email.assert_called_once_with(
        Destination={
            'ToAddresses': [
                test_email,
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
        Source='test_name <test@sender.com>',

    )

    mocked_boto3.assert_called_once_with(
        'ses',
        aws_access_key_id='access_id',
        aws_secret_access_key='access_secret',
        region_name='region',
    )
