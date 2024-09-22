from models.base import Base

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import mapped_column, relationship


class Transactions(Base):
    __tablename__ = 'transactions'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_account_id = mapped_column(Integer, ForeignKey("accounts.id",onupdate="CASCADE")) #transfer
    to_account_id = mapped_column(Integer, ForeignKey("accounts.id", onupdate="CASCADE")) #deposit
    amount = mapped_column(DECIMAL(10,2))
    type = mapped_column(String (255))
    description = mapped_column(String(255))
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())


    account_from = relationship("Accounts", foreign_keys=[from_account_id], back_populates="transactions_from")
    account_to = relationship("Accounts", foreign_keys=[to_account_id], back_populates="transactions_to")
    
    def __repr__(self):
        return f'<Transactions {self.id}>'