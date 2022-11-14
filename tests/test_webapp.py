import os
from datetime import datetime

import pytest
from connect.client import R

from cen import database
from cen.models import EmailTaskPage
from cen.webapp import CENWebApplication


def test_retrieve_email_tasks_not_found(mocker, auto_rollback, test_client_factory):

    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/email_task/RUL-000',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 404


@pytest.mark.freeze_time('2022-10-27')
def test_retrieve_email_tasks(mocker, auto_rollback, test_client_factory):
    task = {
        'installation_id': 'EIN-000',
        'date': datetime.utcnow(),
        'email_from': 'email_from',
        'email_to': 'email_to',
        'product_id': 'product_id',
        'product_name': 'product_name',
        'product_logo': 'product_logo',
        'request_id': 'request_id',
        'asset_id': 'asset_id',
        'body': 'body',
        'email_response': 'email_response',
    }
    obj = database.create_email_task(task)
    expected_task = {
        'id': obj.id,
        'product_id': 'product_id',
        'product_name': 'product_name',
        'product_logo': 'product_logo',
        'date': datetime.utcnow().isoformat(),
        'email_to': 'email_to',
    }
    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/email_tasks',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 200
    data = response.json()
    assert EmailTaskPage(**data).dict() == EmailTaskPage(count=1, results=[expected_task]).dict()


def test_retrieve_settings(test_client_factory, client_mocker_factory):
    installation = {
        'id': 'EIN-123',
        'owner': {'id': 'PA-000-111'},
    }
    brand_data = {
        'customization': {
            'emailName': 'Test email',
            'email': 'test@example.org',
        },
    }
    client = test_client_factory(CENWebApplication)
    client_mocker = client_mocker_factory()
    client_mocker.accounts['PA-000-111'].get(return_value={'brand': 'BR-012'})
    client_mocker.branding('brand').get(return_value=brand_data)
    response = client.get('/api/settings', installation=installation)
    assert response.status_code == 200
    assert response.json() == {'name': 'Test email', 'email_sender': 'test@example.org'}


def test_list_rules(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    obj = database.create_rule(rule)
    expected_rule = {
        'id': obj.id,
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/rules',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 200
    data = response.json()

    assert data == [expected_rule]


def test_get_rule(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    obj = database.create_rule(rule)
    expected_rule = {
        'id': obj.id,
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    url = f'/api/rules/{obj.id}'
    client = test_client_factory(CENWebApplication)
    response = client.get(
        url,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_rule


def test_get_rule_no_exit(mocker, auto_rollback, test_client_factory):

    url = '/api/rules/RUL-000'
    client = test_client_factory(CENWebApplication)
    response = client.get(
        url,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 404


def test_create_rule(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    client = test_client_factory(CENWebApplication)
    response = client.post(
        '/api/rules',
        json=rule,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 201
    data = response.json()
    assert data['enabled'] is True
    assert data['installation_id'] == 'EIN-000'
    assert data['message'] == 'message'
    assert data['product_id'] == 'PRD-000-000-000'
    assert data['product_logo'] == 'logo.svg'
    assert data['product_name'] == 'Product name'


def test_create_rule_bad_template(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': '{{% for item in',
        'enabled': True,
    }
    client = test_client_factory(CENWebApplication)
    response = client.post(
        '/api/rules',
        json=rule,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {'code': 'CEN-002', 'message': 'Syntax error in template parsing'}


def test_create_rule_product_duplicated(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    database.create_rule(rule)
    client = test_client_factory(CENWebApplication)
    response = client.post(
        '/api/rules',
        json=rule,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 400
    data = response.json()
    assert data == {
        'code': 'CEN-001',
        'message': 'A rule for the product PRD-000-000-000 already exist',
    }


def test_delete_rule(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    obj = database.create_rule(rule)
    url = f'/api/rules/{obj.id}'
    client = test_client_factory(CENWebApplication)
    response = client.delete(
        url,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 204


def test_delete_rule_no_exist(mocker, auto_rollback, test_client_factory):
    client = test_client_factory(CENWebApplication)
    response = client.delete(
        '/api/rules/RUL-0000',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 404


def test_update_rule(mocker, auto_rollback, test_client_factory):
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }

    new_rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message2',
        'enabled': False,
    }
    obj = database.create_rule(rule)
    url = f'/api/rules/{obj.id}'
    client = test_client_factory(CENWebApplication)
    response = client.put(
        url,
        json=new_rule,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['enabled'] is False
    assert data['message'] == 'message2'


def test_update_rule_no_exist(mocker, auto_rollback, test_client_factory):

    new_rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-000',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message2',
        'enabled': False,
    }
    client = test_client_factory(CENWebApplication)
    response = client.put(
        '/api/rules/RUL-0000',
        json=new_rule,
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 404


def test_retrieve_products(test_client_factory, client_mocker_factory, auto_rollback):
    product1 = {
        'id': 'PRD-000-000-001',
        'name': 'Product P01',
        'icon': 'icon1.svg',
    }

    product2 = {
        'id': 'PRD-000-000-002',
        'name': 'Product P02',
    }

    client_mocker = client_mocker_factory()
    query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)
    client_mocker.collection('products').filter(query).mock(
        return_value=[product1, product2],
    )
    rule = {
        'installation_id': 'EIN-000',
        'product_id': 'PRD-000-000-001',
        'product_name': 'Product name',
        'product_logo': 'logo.svg',
        'message': 'message',
        'enabled': True,
    }
    database.create_rule(rule)

    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/products',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 200
    data = response.json()
    products = {product['id']: product for product in data}
    assert len(products) == 2
    assert product1['id'] in products
    assert product2['id'] in products
    assert products[product1['id']]['used'] is True
    assert products[product2['id']]['used'] is False
    assert products[product1['id']]['icon'] == 'icon1.svg'
    assert products[product2['id']]['icon'] == './images/product.svg'


def test_get_product(test_client_factory, client_mocker_factory, auto_rollback):

    product = {
        'id': 'PRD-000-000-001',
        'name': 'Product P01',
        'icon': 'icon1.svg',
    }
    product_id = 'PRD-000'
    client_mocker = client_mocker_factory()
    client_mocker.collection('products')[product_id].get(return_value=product)

    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/products/PRD-000',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 200
    assert response.json() == product


def test_get_product_not_found(test_client_factory, client_mocker_factory, auto_rollback):

    product_id = 'PRD-000'
    client_mocker = client_mocker_factory()
    client_mocker.collection('products')[product_id].get(status_code=404)

    client = test_client_factory(CENWebApplication)
    response = client.get(
        '/api/products/PRD-000',
        config={'DB_CONNECTION_STRING': os.getenv('TEST_DATABASE_URL')},
    )
    assert response.status_code == 404
