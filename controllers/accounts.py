from flask import Blueprint, request
from connectors.mysql_connector import connection
from models.accounts import Accounts

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from flask_login import login_required, current_user

from cerberus import Validator
from validation.accounts_insert import accounts_insert_schema

accounts_routes = Blueprint("accounts_routes", __name__)

@accounts_routes.route("/accounts", methods=["POST"])
@login_required
def register_accounts():
    
    v = Validator(accounts_insert_schema)
    request_body = {
        "account_type" : request.form["account_type"],
        "account_number" : request.form["account_number"],
        "balance" : request.form["balance"]
    }
    
    if not v.validate(request_body):
        return {"error": v.errors}, 409
    
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        NewAccounts = Accounts(
            account_type=request.form["account_type"],
            account_number=request.form["account_number"],
            balance=request.form["balance"],
            user_id=current_user.id
        )
        s.add(NewAccounts)
        s.commit()
    except Exception as e:
        s.rollback()
        return { "message": "Fail to Register", "error":str(e)}, 500
    finally:
        s.close()
    return { "message": "Register Success" }, 200
    


@accounts_routes.route("/accounts", methods=['GET'])
@login_required
def accounts_list():
    Session = sessionmaker(connection)
    s = Session()

    try:
        # Query untuk mengambil akun yang terkait dengan current_user
        accounts_query = select(Accounts).where(Accounts.user_id == current_user.id)
        result = s.execute(accounts_query)
        accounts = []

        for row in result.scalars():
            accounts.append({
                "username": current_user.username,
                "id": row.id,
                "account_type": row.account_type,
                "account_number": row.account_number,
                "balance": row.balance,
            })

        return {
            'accounts': accounts,
            'message' : "This is your account list, " + current_user.username
        }
    except Exception as e:
        return { 'message': "Unexpected Error", "error":str(e) }, 500
    finally:
        s.close()

        
@accounts_routes.route("/accounts/<id>", methods=['GET'])
@login_required
def accounts_specific(id):
    Session = sessionmaker(connection)
    s = Session()

    try:
        # Query to fetch account details matching the given id and current user
        accounts_query = select(Accounts).where(
            (Accounts.id == id) &
            (Accounts.user_id == current_user.id)
        )
        
        result = s.execute(accounts_query)
        account = result.scalars().first()

        if account:
            account_data = {
                "username": current_user.username,
                "id": account.id,
                "account_type": account.account_type,
                "account_number": account.account_number,
                "balance": account.balance,
            }
            return {
                'account': account_data,
                'message': "This is Your Account Detail, " + current_user.username
            }
        else:
            return {'message': "Accounts not found or not authorized"}, 404
    except Exception as e:
        return {'message': "Unexpected Error", "error": str(e)}, 500
    finally:
        s.close()

        

@accounts_routes.route("/accounts/<id>", methods=['PUT'])
@login_required
def accounts_update(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        accounts = s.query(Accounts).filter(Accounts.id == id, Accounts.user_id == current_user.id).first()

        accounts.account_type = request.form['account_type']
        accounts.account_number = request.form['account_number']

        s.commit()
    except Exception as e:
        s.rollback()
        return { "message": "Fail to Update", "error":str(e)}, 500
    finally:
        s.close()
    return { 'message': 'Success update Accounts data'}, 200

    
@accounts_routes.route('/accounts/<id>', methods=['DELETE'])
@login_required
def accounts_delete(id):
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    try:
        accounts = s.query(Accounts).filter(Accounts.id == id).first()
        
        if not accounts:
            return { "message": "Accounts not found" }, 404
        
        if current_user.id != accounts.user_id:
            return { "message": "Unauthorized: You are not authorized to delete this accounts" }, 403
        s.delete(accounts)
        s.commit()
    except Exception as e:

        s.rollback()
        return { "message": "Fail to Delete", "error": str(e)}, 500
    finally : 
        s.close()
    
    return { 'message': 'Success delete Accounts'}, 200


# user = s.query(User).filter_by(email=email).first()
# accounts = user.accounts

# transaction = s.query(Transaction).filter_by(email=email)first()
# userFrom = transaction.user.username

# transaction = s.query(Transaction).filter_by(email=email, id=id),first()
# userFrom = transaction.user.username