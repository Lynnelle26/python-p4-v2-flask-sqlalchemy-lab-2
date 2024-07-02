from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reviews = relationship("Review", back_populates="customer")
    items = association_proxy('reviews', 'item')

    serialize_rules = (
        ('id', dict(by_value=True)),
        ('name', dict(by_value=True)),
        ('items', dict(by_Related()),  # avoid recursion
            serialize_only=(lambda o: [i.serialize() for i in o]))
    )


    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    reviews = relationship("Review", back_populates="item")

    serialize_rules = (
        ('id', dict(by_value=True)),
        ('name', dict(by_value=True)),
        ('price', dict(by_value=True)),
        ('reviews', dict(only=('id', 'comment'), by_value=True))  # exclude item.reviews
    )

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    customer = relationship("Customer", back_populates="reviews")
    item = relationship("Item", back_populates="reviews")

    serialize_rules = (
        ('id', dict(by_value=True)),
        ('comment', dict(by_value=True)),
        ('customer', dict(only=('id', 'name'), by_value=True)),  # exclude reviews.customer
        ('item', dict(only=('id', 'name'), by_value=True))  # exclude reviews.item
    )

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'