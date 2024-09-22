from models.base import Base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy import func
from models.transactions import Transactions

class Accounts(Base):
    __tablename__ = "accounts"
    
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_type = mapped_column(String(255))
    account_number = mapped_column(String(255), unique=True)
    balance = mapped_column(DECIMAL(10,2))
    user_id = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="accounts")
    transactions_from = relationship("Transactions", foreign_keys="[Transactions.from_account_id]", cascade="all,delete-orphan", back_populates="account_from")
    transactions_to = relationship("Transactions", foreign_keys="[Transactions.to_account_id]", cascade="all,delete-orphan", back_populates="account_to")
    def __repr__(self):
        return f'<Accoount {self.id}>'