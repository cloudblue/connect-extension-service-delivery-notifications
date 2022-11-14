import os

import pytest
from connect.client import AsyncConnectClient, ConnectClient

from cen import database


@pytest.fixture(scope='session', autouse=True)
def init_db():
    url = os.getenv('TEST_DATABASE_URL')
    database.initialize(url)


@pytest.fixture
def connect_client():
    return ConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://example.org/public/v1',
    )


@pytest.fixture
def async_connect_client():
    return AsyncConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://localhost/public/v1',
    )


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def auto_rollback(mocker):
    mocker.patch('cen.database.initialize')
    mocker.patch('cen.database.close')
    mocker.patch('cen.database.reset_state')

    with database.db.transaction() as txn:
        try:
            yield
        finally:
            txn.rollback()


@pytest.fixture
def installation_data():
    return {
        'id': 'EIN-000',
        'owner': {'id': 'PA-000'},
    }


@pytest.fixture
def request_data():
    return {
        'id': 'PR-000',
        'asset': {
            'id': 'AS-0000',
            'product': {
                'id': 'PRD-000',
                'name': 'Product name',
                'icon': 'logo.svg',
            },
            'tiers': {
                'customer': {
                    'contact_info': {
                        'contact': {'email': 'recipient@customer.org'},
                    },
                },
            },
        },
    }


@pytest.fixture
def rule_data():
    return {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }


@pytest.fixture
def rule_data_bad_template():
    return {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': '{%message',
        'enabled': True,
    }
