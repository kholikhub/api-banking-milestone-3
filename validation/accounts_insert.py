accounts_insert_schema = {
    'account_type' : { 'type': 'string', 'required': True, 'empty': False},
    'account_number' : { 'type': 'string', 'required': True, 'minlength': 6},
    'balance': {'type': 'string', 'required': True, 'regex': '^[0-9]+$'}
}