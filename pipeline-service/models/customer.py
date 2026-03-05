from sqlalchemy import Column, String, Text, Date, Numeric, DateTime
from sqlalchemy.sql import func
from database import Base


class Customer(Base):
    __tablename__ = 'customers'

    customer_id = Column(String(50), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    account_balance = Column(Numeric(15, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name={self.first_name} {self.last_name})>"

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'account_balance': float(self.account_balance) if self.account_balance else 0.00,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
