from flask import Blueprint, request
from connectors.mysql_connector import connection
from models.transactions import Transactions
from models.accounts import Accounts
from decimal import Decimal, InvalidOperation
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from flask_login import login_required, current_user\

from cerberus import Validator
from validation.transactions import transactions_schema

transaction_routes = Blueprint("transaction_routes", __name__)

@transaction_routes.route('/transactions', methods=['POST'])
@login_required
def transactions():
    
    v = Validator(transactions_schema)
    request_body = {
        "type" : request.form["type"],
        "from_account_id" : request.form["from_account_id"],
        "amount_str" : request.form["amount"],
        "description" : request.form["description"]
    }
    
    if not v.validate(request_body):
        return {"error": v.errors}, 409
    
    Session = sessionmaker(connection)
    s = Session()
    
    s.begin()
    try:
        type = request.form["type"]
        from_account_id = request.form['from_account_id']
        amount_str = request.form['amount']
        description = request.form.get("description")

        # Validasi dan konversi amount ke Decimal
        try:
            amount = Decimal(amount_str)
        except InvalidOperation:
            return {'message': 'Invalid amount format'}, 400

        if type == 'deposit':
            accounts = s.query(Accounts).filter_by(id=from_account_id).first()
            
            if not accounts:
                return {"message": "Account not found"}, 404

            if current_user.id != accounts.user_id:
                return {"message": "Unauthorized: You only can deposit to your accounts"}, 403

            new_transaction = Transactions(
                from_account_id=from_account_id,
                amount=amount,
                type="deposit",
                description=description
            )

            s.add(new_transaction)
            
            accounts.balance = Decimal(accounts.balance) + amount

            s.commit()
            return {'message': 'Deposit successful', 'transaction_id': new_transaction.id}, 201
        
        if type == 'withdrawal':
            from_account_id = request.form['from_account_id']
            amount = Decimal(request.form['amount'])  # Pastikan amount diubah menjadi Decimal atau sesuai tipe yang digunakan

            # Ambil akun
            account = s.query(Accounts).filter_by(id=from_account_id).first()

            if not account:
                return {"message": "Account not found"}, 404

            if amount > account.balance:
                return {"message": "Failed withdrawal: Amount exceeds balance"}, 400

            # Lakukan transaksi penarikan
            new_transaction = Transactions(
                from_account_id=from_account_id,
                amount=amount,
                type="withdrawal",
                description=description
            )

            s.add(new_transaction)
            
            account.balance = account.balance - amount  # Kurangi balance

            s.commit()
            return {'message': 'Withdrawal successful', 'transaction_id': new_transaction.id}, 201
        
        elif type == 'transfer':
            from_account_id = request.form['from_account_id']
            to_account_id = request.form['to_account_id']
            amount = Decimal(request.form['amount'])  # Pastikan amount diubah menjadi Decimal atau sesuai tipe yang digunakan

            # Ambil akun pengirim dan penerima
            from_account = s.query(Accounts).filter_by(id=from_account_id).first()
            to_account = s.query(Accounts).filter_by(id=to_account_id).first()

            if not from_account or not to_account:
                s.rollback()
                return {'message': 'One or both accounts not found'}, 404

            if from_account.balance < amount:
                s.rollback()
                return {'message': 'Failed transfer: Insufficient balance'}, 400

            # Lakukan transfer
            new_transaction = Transactions(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                type='transfer',
                description=description
            )

            s.add(new_transaction)

            # Kurangi saldo dari akun pengirim dan tambahkan ke akun penerima
            from_account.balance -= amount
            to_account.balance += amount

            s.commit()
            return {'message': 'Transfer successful', 'transaction_id': new_transaction.id}, 201
        
        else:
            return {'message': 'Transaction type not supported'}, 400

    except Exception as e:
        s.rollback()
        return {'message': 'Transaction failed', 'error': str(e)}, 500
    finally:
        s.close()

@transaction_routes.route('/transactions', methods=['GET'])
@login_required
def get_all_transactions():
    Session = sessionmaker(connection)
    s = Session()
    
    try:
        transaction_query = select(Transactions)
        result = s.execute(transaction_query)
        transaction_list = []
        
        for row in result.scalars():
            transaction_list.append({
                'id': row.id,
                'from_account_id': row.from_account_id if row.from_account_id is not None else 0 ,
                'to_account_id': row.to_account_id if row.to_account_id is not None else 0 ,
                'amount': str(row.amount),
                'type': row.type,
                'description': row.description,
            })
        return (transaction_list ), 200
    except Exception as e:
        return ({'message': 'Failed to retrieve transactions', 'error': str(e)}), 500
    finally:
        s.close()
        
@transaction_routes.route('/transactions/<id>', methods=['GET'])
@login_required
def get_transaction_by_id(id):
    Session = sessionmaker(connection)
    s = Session()
    
    try:
        transaction_query = s.query(Transactions).filter_by(id=id).first()
        if not transaction_query:
            return ({'message': 'Transaction not found'}), 404
        
        transaction_data = {
            'id': transaction_query.id,
            'to_account_id': transaction_query.to_account_id,
            'amount': str(transaction_query.amount),
            'type': transaction_query.type,
            'description': transaction_query.description,
        }
        return (transaction_data), 200
    except Exception as e:
        return ({'message': 'Failed to retrieve transaction', 'error': str(e)}), 500
    finally:
        s.close()