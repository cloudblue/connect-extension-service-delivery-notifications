from connect.eaas.core.enums import ResultType

from cen import database, mail
from cen.events import EmailNotificationsEventsApplication


def test_send_email(
    mocker,
    client_mocker_factory,
    auto_rollback,
    connect_client,
    logger,
    installation_data,
    request_data,
    rule_data,
):
    client_mocker = client_mocker_factory()
    client_mocker.accounts['PA-000'].get(return_value={'brand': 'BR-000'})
    client_mocker.branding('brand').get(return_value={
        'customization': {
            'email': 'test@example.com',
            'emailName': 'testname',
        }},
    )

    database.create_rule(rule_data)
    mocked_ses_client = mocker.MagicMock()
    mocked_boto3 = mocker.patch('cen.events.boto3.client', return_value=mocked_ses_client)
    mocked_jinja = mocker.patch('cen.events.jinja.render', return_value='rendered body')

    app = EmailNotificationsEventsApplication(
        connect_client,
        logger,
        {
            'DB_CONNECTION_STRING': 'connection_string',
            'AWS_ACCESS_KEY_ID': 'access_id',
            'AWS_SECRET_ACCESS_FOR_SES': 'access_secret',
            'AWS_REGION': 'region',
        },
        installation=installation_data,
        installation_client=connect_client,
    )
    result = mail.send_email(request_data)
    assert result.status == ResultType.SUCCESS

    mocked_ses_client.send_email.assert_called_once_with(
        Destination={
            'ToAddresses': [
                request_data['asset']['tiers']['customer']['contact_info']['contact']['email'],
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': '<p>rendered body</p>',
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': f"New subscription for product {request_data['asset']['product']['id']}",
            },
        },
        Source='testname <test@example.com>',
    )


    mocked_boto3.assert_called_once_with(
        'ses',
        aws_access_key_id='access_id',
        aws_secret_access_key='access_secret',
        region_name='region',
    )

    mocked_jinja.assert_called_once_with(
        rule_data['message'],
        request_data,
    )

