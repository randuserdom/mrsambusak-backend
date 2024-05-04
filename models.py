from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True)
    online = Column(Boolean, default=False)
    password_hash = Column(String)

    # Establish one-to-many relationship with Message model
    messages = relationship("Message", back_populates="sender")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.id"))  # Foreign key constraint
    content = Column(String)

    # Establish relationship with User model
    sender = relationship("User", back_populates="messages")
