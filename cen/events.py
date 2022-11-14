from datetime import datetime

import boto3
import markdown
import peewee
from connect.eaas.core.decorators import event, variables
from connect.eaas.core.extension import EventsApplicationBase
from connect.eaas.core.responses import BackgroundResponse

from cen import database, jinja
from cen.database import create_email_task, get_rule_product

CHARSET = 'UTF-8'


@variables(
    [
        {
            'name': 'AWS_SECRET_ACCESS',
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
    ],
)
class CENEventsApplication(EventsApplicationBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        database.initialize(self.config['DB_CONNECTION_STRING'])

    @event('asset_purchase_request_processing', statuses=['approved'])
    def send_email_notification(self, request):
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=self.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=self.config['AWS_SECRET_ACCESS'],
            region_name=self.config['AWS_REGION'],
        )

        account_id = self.installation['owner']['id']
        result_brand = self.installation_client.accounts[account_id].get()
        brand = result_brand['brand']
        body = self.installation_client.branding('brand').get(params={'id': brand})

        name_from = body['customization']['emailName']
        email_from = self.config.get('TEST_EMAIL_FROM', body['customization']['email'])

        email_source = f'{name_from} <{email_from}>'
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
            return BackgroundResponse.fail('No template found')

        try:
            body = markdown.markdown(jinja.render(template_source, request))
        except Exception as e:
            self.logger.info(f'Error in template: {e}')
            return BackgroundResponse.fail(str(e))

        self.logger.info(f'Send the email for {request["id"]}')
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
        installation_id = self.installation['id']
        response_email = response_email['ResponseMetadata']['RequestId']
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
