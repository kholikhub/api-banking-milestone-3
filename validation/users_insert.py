users_insert_schema = {
    'username' : { 'type': 'string', 'required': True, 'empty': False},
    'email' : { 'type': 'string', 'required': True, 'minlength': 3},
    'password_hash': { 'type': 'string', 'required': True, 'minlength': 6}
}