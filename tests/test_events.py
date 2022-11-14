from connect.eaas.core.enums import ResultType

from cen import database
from cen.events import CENEventsApplication


def test_constructor(mocker, connect_client, logger):
    mocked_initialize = mocker.patch('cen.events.database.initialize')
    CENEventsApplication(
        connect_client,
        logger,
        {'DB_CONNECTION_STRING': 'connection_string'},
    )
    mocked_initialize.assert_called_once_with('connection_string')


def test_send_email_notification(
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

    app = CENEventsApplication(
        connect_client,
        logger,
        {
            'DB_CONNECTION_STRING': 'connection_string',
            'AWS_ACCESS_KEY_ID': 'access_id',
            'AWS_SECRET_ACCESS': 'access_secret',
            'AWS_REGION': 'region',
        },
        installation=installation_data,
        installation_client=connect_client,
    )
    result = app.send_email_notification(request_data)
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

    count, email_tasks = database.get_email_tasks(installation_data['id'], '', limit=100, offset=0)
    assert count == 1

    email_task = database.get_email_task(installation_data['id'], email_tasks[0].id)
    assert email_task.email_to == 'recipient@customer.org'
    assert email_task.email_from == 'test@example.com'
    assert email_task.product_id == 'PRD-000'
    assert email_task.product_name == 'Product name'
    assert email_task.product_logo == 'logo.svg'
    assert email_task.body == '<p>rendered body</p>'
    assert email_task.request_id == 'PR-000'
    assert email_task.asset_id == 'AS-0000'

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


def test_send_email_notification_error_no_template(
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

    app = CENEventsApplication(
        connect_client,
        logger,
        {
            'DB_CONNECTION_STRING': 'connection_string',
            'AWS_ACCESS_KEY_ID': 'access_id',
            'AWS_SECRET_ACCESS': 'access_secret',
            'AWS_REGION': 'region',
        },
        installation=installation_data,
        installation_client=connect_client,
    )
    result = app.send_email_notification(request_data)
    assert result.status == ResultType.FAIL


def test_send_email_notification_error_template(
    mocker,
    client_mocker_factory,
    auto_rollback,
    connect_client,
    logger,
    installation_data,
    request_data,
    rule_data_bad_template,
):
    client_mocker = client_mocker_factory()
    client_mocker.accounts['PA-000'].get(return_value={'brand': 'BR-000'})
    client_mocker.branding('brand').get(return_value={
        'customization': {
            'email': 'test@example.com',
            'emailName': 'testname',
        }},
    )

    database.create_rule(rule_data_bad_template)
    mocked_ses_client = mocker.MagicMock()
    mocker.patch('cen.events.boto3.client', return_value=mocked_ses_client)

    app = CENEventsApplication(
        connect_client,
        logger,
        {
            'DB_CONNECTION_STRING': 'connection_string',
            'AWS_ACCESS_KEY_ID': 'access_id',
            'AWS_SECRET_ACCESS': 'access_secret',
            'AWS_REGION': 'region',
        },
        installation=installation_data,
        installation_client=connect_client,
    )
    result = app.send_email_notification(request_data)
    assert result.status == ResultType.FAIL

    mocked_ses_client.send_email.assert_not_called()
