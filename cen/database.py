from contextvars import ContextVar
import random

import peewee
from playhouse import db_url

db_state_default = {
    'closed': None,
    'conn': None,
    'ctx': None,
    'transactions': None,
    'autorollback': True,
}
db_state = ContextVar('db_state', default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__('_state', db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = peewee.PostgresqlDatabase(None)
db._state = PeeweeConnectionState()


def initialize(url):
    db.init(**db_url.parse(url))
    db.connect()
    db.create_tables([EmailTask, Rule])
    return db


def close():
    if not db.is_closed():
        db.close()


def reset_state():
    db._state._state.set(db_state_default.copy())
    db._state.reset()


def get_numeric_string(size):
    return str(random.randint(1 * 10 ** (size - 1), 1 * 10 ** size - 1))


class BaseDbModel(peewee.Model):
    MAX_PK_ITERATIONS = 10

    id = peewee.CharField(primary_key=True)

    def save(self, *args, **kwargs):
        if not self.id:
            kwargs.pop('force_insert', None)
            for _ in range(self.MAX_PK_ITERATIONS):
                self.id = (
                    f'{self.PREFIX}-{get_numeric_string(4)}-'
                    f'{get_numeric_string(4)}-{get_numeric_string(4)}'
                )

                try:
                    return super().save(*args, force_insert=True)
                except peewee.IntegrityError as e:
                    if '(id)=' not in str(e.orig):
                        raise e
            raise Exception(f'Cannot generate PK after {self.MAX_PK_ITERATIONS} iterations.')
        return super().save(*args, **kwargs)

    class Meta:
        database = db


class Rule(BaseDbModel):
    PREFIX = 'RUL'

    installation_id = peewee.CharField(index=True)
    product_id = peewee.CharField(index=True)
    product_name = peewee.CharField()
    product_logo = peewee.CharField()
    message = peewee.TextField()
    enabled = peewee.BooleanField()

    class Meta:
        indexes = (
            (('installation_id', 'product_id'), True),
        )


class EmailTask(BaseDbModel):
    PREFIX = 'TSK'

    installation_id = peewee.CharField(index=True)
    date = peewee.DateTimeField(index=True)
    body = peewee.TextField()
    email_from = peewee.CharField()
    email_response = peewee.CharField()
    email_to = peewee.CharField()
    product_id = peewee.CharField()
    product_name = peewee.CharField()
    product_logo = peewee.CharField()
    request_id = peewee.CharField()
    asset_id = peewee.CharField()


def get_all_rules(installation_id):
    result = Rule.select().where(Rule.installation_id == installation_id)
    return result


def get_rule(installation_id, rule_id):
    result = Rule.get((Rule.id == rule_id) & (Rule.installation_id == installation_id))
    return result


def get_rule_product(installation_id, product_id):
    result = Rule.get(
        (Rule.product_id == product_id)
        & (Rule.installation_id == installation_id)
        & (Rule.enabled == True),  # noqa: E712
    )
    return result


def create_rule(rule):
    dbrule = Rule(**rule)
    dbrule.save()
    return dbrule


def update_rule(rule_id, rule):
    db_rule = get_rule(rule.installation_id, rule_id)
    print(f'===Rule ID {rule_id}====')
    print(f'===Rule Enabled {rule.enabled}====')

    db_rule.message = rule.message
    db_rule.enabled = rule.enabled
    result = db_rule.save()
    print(f'===Result {result}====')
    return db_rule


def delete_rule(installation_id, rule_id):
    return Rule.delete().where(
        (Rule.id == rule_id)
        & (Rule.installation_id == installation_id),
    ).execute()


def create_email_task(email_task):
    dbemailtask = EmailTask(**email_task)
    dbemailtask.save()
    return dbemailtask


def get_email_tasks(installation_id, search, limit, offset):
    result = EmailTask.select(
        EmailTask.id,
        EmailTask.product_id,
        EmailTask.product_name,
        EmailTask.product_logo,
        EmailTask.email_to,
        EmailTask.date,
    ).where(
        EmailTask.installation_id == installation_id,
        (EmailTask.product_id.contains(search)
            | EmailTask.email_to.contains(search)),

    ).limit(limit).offset(offset)
    count = EmailTask.select().where(
        EmailTask.installation_id == installation_id,
        (EmailTask.product_id.contains(search)
            | EmailTask.email_to.contains(search)),
    ).count()
    return count, result


def get_email_task(installation_id, task_id):
    result = EmailTask.get(
        (EmailTask.id == task_id)
        & (EmailTask.installation_id == installation_id),
    )
    return result
