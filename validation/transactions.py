transactions_schema = {
    'type' : { 'type': 'string', 'required': True, 'empty': False},
    'from_account_id' : { 'type': 'string', 'required': True, 'regex': '^[0-9]+$'},
    'amount_str': {'type': 'string', 'required': True, 'regex': '^[0-9]+$'},
    'description': {'type': 'string', 'required': True, 'empty': False}
}