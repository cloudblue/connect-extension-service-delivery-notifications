import os

from cen import mail

from unittest.mock import ANY


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
    product_id = 'PRD-000'

    mocked_ses_client = mocker.MagicMock()
    mocked_boto3 = mocker.patch('cen.mail.boto3.client', return_value=mocked_ses_client)
    mail.send_email(config, test_sender, test_name, test_email, body, product_id)
    mocked_ses_client.send_raw_email.assert_called_once_with(
        Source=f'{test_name} <{test_sender}>',
        Destinations=[test_email],
        RawMessage={
            'Data': ANY,
        },
    )

    mocked_boto3.assert_called_once_with(
        'ses',
        aws_access_key_id='access_id',
        aws_secret_access_key='access_secret',
        region_name='region',
    )
