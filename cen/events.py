from datetime import datetime

import markdown
import peewee
from connect.eaas.core.decorators import event, variables
from connect.eaas.core.extension import EventsApplicationBase
from connect.eaas.core.responses import BackgroundResponse

from cen import database, jinja, mail
from cen.database import create_email_task, get_rule_product

CHARSET = 'UTF-8'


@variables(
    [
        {
            'name': 'AWS_SECRET_ACCESS_FOR_SES',
            'initial_value': 'Change for the secret',
            'secure': True,
        },
        {
            'name': 'AWS_ACCESS_KEY_ID',
            'initial_value': 'Change for the access key',
        },
        {
            'name': 'AWS_REGION',
            'initial_value': 'Change for the region',
        },
        {
            'name': 'DB_CONNECTION_STRING',
            'initial_value': 'Change for the database chain connection',
            'secure': True,
        },
        {
            'name': 'ENVIRONMENT',
            'initial_value': 'TEST',
        },
    ],
)
class EmailNotificationsEventsApplication(EventsApplicationBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        database.initialize(self.config['DB_CONNECTION_STRING'])

    @event('asset_purchase_request_processing', statuses=['approved'])
    def send_email_notification(self, request):

        account_id = self.installation['owner']['id']
        result_brand = self.installation_client.accounts[account_id].get()
        brand = result_brand['brand']
        body = self.installation_client.branding('brand').get(params={'id': brand})
        email_from_name = body['customization']['emailName']
        email_from = self.config.get('TEST_EMAIL_FROM', body['customization']['email'])

        email_to = request['asset']['tiers']['customer']['contact_info']['contact']['email']
        request_id = request['id']
        asset_id = request['asset']['id']
        template_source = None
        installation_id = self.installation['id']
        product_id = request['asset']['product']['id']
        product_name = request['asset']['product']['name']
        product_logo = request['asset']['product'].get('icon', './images/product.svg')

        try:
            template_source = get_rule_product(installation_id, product_id).message
        except peewee.DoesNotExist:
            self.logger.info(f'No template found for product {product_id} and {installation_id}')
            return BackgroundResponse.done()

        try:
            body = markdown.markdown(jinja.render(template_source, request))
        except Exception as e:
            self.logger.info(f'Error in template: {e}')
            return BackgroundResponse.done()

        response_email = mail.send_email(
            self.config,
            email_from,
            email_from_name,
            email_to,
            body,
            product_id,
        )
        item = {
            'installation_id': installation_id,
            'date': datetime.utcnow(),
            'email_from': email_from,
            'email_to': email_to,
            'product_id': product_id,
            'product_name': product_name,
            'product_logo': product_logo,
            'request_id': request_id,
            'asset_id': asset_id,
            'body': body,
            'email_response': response_email,
        }

        create_email_task(item)
        return BackgroundResponse.done()
