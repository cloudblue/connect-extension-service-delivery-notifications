from datetime import datetime
from typing import Any, List

from connect.client import ConnectClient, R
from fastapi import Depends, Response, status
from fastapi.responses import JSONResponse
from peewee import DoesNotExist, IntegrityError
from connect.eaas.core.decorators import account_settings_page, module_pages, router, web_app
from connect.eaas.core.extension import WebApplicationBase
from connect.eaas.core.inject.synchronous import get_installation, get_installation_client
from connect.eaas.core.inject.common import get_call_context, get_config
from connect.eaas.core.inject.models import Context

from cen.models import EmailLog, EmailLogPage, Error, Product, Rule, Settings
from cen import database, jinja, mail


async def reset_db_state():
    database.reset_state()


def get_db(db_state=Depends(reset_db_state), config=Depends(get_config)):
    try:
        database.initialize(config['DB_CONNECTION_STRING'])
        yield
    finally:
        database.close()


@web_app(router)
@account_settings_page('Settings', '/static/settings.html')
@module_pages(
    'Log',
    '/static/index.html',
)
class EmailNotificationsWebApplication(WebApplicationBase):

    @router.get(
        '/rules',
        response_model=List[Rule],
    )
    def list_rules(self, context: Context = Depends(get_call_context), db=Depends(get_db)):
        return list(database.get_all_rules(context.installation_id))

    @router.post(
        '/rules',
        status_code=status.HTTP_201_CREATED,
        response_model=Rule,
        responses={status.HTTP_400_BAD_REQUEST: {'model': Error}},
    )
    def create_rule(
        self, rule: Rule,
        context: Context = Depends(get_call_context),
        db: Any = Depends(get_db),
    ):
        rule.installation_id = context.installation_id
        if not jinja.validate(rule.message):
            content = {'code': 'CEN-002', 'message': 'Syntax error in template parsing'}
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
        try:
            return database.create_rule(rule.dict())
        except IntegrityError:
            content = {
                'code': 'CEN-001',
                'message': f'A rule for the product {rule.product_id} already exist',
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)

    @router.put(
        '/rules/{rule_id}',
        status_code=status.HTTP_200_OK,
        response_model=Rule,
        responses={status.HTTP_400_BAD_REQUEST: {'model': Error}},
    )
    def update_rule(
        self,
        rule_id,
        rule: Rule,
        response: Response,
        context: Context = Depends(get_call_context),
        db=Depends(get_db),
    ):
        rule.installation_id = context.installation_id
        try:
            return database.update_rule(rule_id, rule)
        except DoesNotExist:
            response.status_code = status.HTTP_404_NOT_FOUND

    @router.delete('/rules/{rule_id}', status_code=status.HTTP_204_NO_CONTENT)
    def del_rule(
        self,
        rule_id,
        response: Response,
        context: Context = Depends(get_call_context),
        db=Depends(get_db),
    ):
        delete_count = database.delete_rule(context.installation_id, rule_id)
        if not delete_count:
            response.status_code = status.HTTP_404_NOT_FOUND

    @router.get(
        '/rules/{rule_id}',
        response_model=Rule,
    )
    def get_rule(
        self,
        rule_id,
        response: Response,
        context: Context = Depends(get_call_context),
        db=Depends(get_db),
    ):
        try:
            return database.get_rule(context.installation_id, rule_id)
        except DoesNotExist:
            response.status_code = status.HTTP_404_NOT_FOUND

    @router.get('/products/{product_id}', response_model=Product)
    def retrieve_product(
        self,
        product_id,
        installation_client: ConnectClient = Depends(get_installation_client),
    ):
        return Product(**installation_client.products[product_id].get())

    @router.get('/products')
    def retrieve_rules_products(
        self,
        context: Context = Depends(get_call_context),
        installation_client: ConnectClient = Depends(get_installation_client),
        db=Depends(get_db),
    ):
        rule_id = []
        rules = database.get_all_rules(context.installation_id)
        for rule in rules:
            rule_id.append(rule.product_id)
        query = R().visibility.listing.eq(True) | R().visibility.syndication.eq(True)
        products = []
        for product in installation_client.collection('products').filter(query):
            icon = product.get('icon', './images/product.svg')
            products.append({
                'id': product['id'],
                'name': product['name'],
                'icon': icon,
                'used': product['id'] in rule_id,
            })
        return products

    @router.get(
        '/email_tasks',
        response_model=EmailLogPage,
    )
    def retrieve_email_tasks(
        self,
        search: str = '',
        limit: int = 100,
        offset: int = 0,
        context: Context = Depends(get_call_context),
        db: Any = Depends(get_db),
    ):
        count, results = database.get_email_tasks(
            context.installation_id,
            search,
            limit,
            offset,
        )
        return EmailLogPage(count=count, results=list(results))

    @router.get(
        '/email_task/{task_id}',
        response_model=EmailLog,
    )
    def retrieve_email_task(
        self,
        task_id,
        response: Response,
        context: Context = Depends(get_call_context),
        db: Any = Depends(get_db),
    ):
        try:
            return database.get_email_task(context.installation_id, task_id)
        except DoesNotExist:
            response.status_code = status.HTTP_404_NOT_FOUND

    @router.get('/settings')
    def retrieve_settings(
        self,
        installation: dict = Depends(get_installation),
        installation_client: ConnectClient = Depends(get_installation_client),
    ) -> Settings:
        account_id = installation['owner']['id']
        result_brand = installation_client.accounts[account_id].get()
        brand = result_brand['brand']
        body = installation_client.branding('brand').get(params={'id': brand})

        name = body['customization']['emailName']
        email = body['customization']['email']

        return {'name': name, 'email_sender': email}

    @router.post(
        '/tasks/{task_id}/resend',
        response_model=EmailLog,
    )
    def resend_email(
        self,
        task_id,
        response: Response,
        config: dict = Depends(get_config),
        installation: dict = Depends(get_installation),
        installation_client: ConnectClient = Depends(get_installation_client),
        db: Any = Depends(get_db),
    ):
        try:
            task = database.get_email_task(installation['id'], task_id)
            account_id = installation['owner']['id']
            result_brand = installation_client.accounts[account_id].get()
            brand = result_brand['brand']
            body = installation_client.branding('brand').get(params={'id': brand})
            email_from_name = body['customization']['emailName']
            email_from = config.get('TEST_EMAIL_FROM', body['customization']['email'])

            email_response = mail.send_email(
                config,
                email_from,
                email_from_name,
                task.email_to,
                task.body,
                task.product_id,
            )
            item = {
                'installation_id': task.installation_id,
                'date': datetime.utcnow(),
                'email_from': email_from,
                'email_to': task.email_to,
                'product_id': task.product_id,
                'product_name': task.product_name,
                'product_logo': task.product_logo,
                'request_id': task.request_id,
                'asset_id': task.asset_id,
                'body': task.body,
                'email_response': email_response,
            }
            new_task = database.create_email_task(item)
            return new_task

        except DoesNotExist:
            response.status_code = status.HTTP_404_NOT_FOUND
