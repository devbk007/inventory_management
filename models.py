from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    product_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def serialize(self):
        return {
            'id': self.product_id,
            'name': self.name
        }

class Location(db.Model):
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def serialize(self):
        return {
            'location_id': self.location_id,
            'name': self.name
        }

class ProductQuantity(db.Model):
    product_quantity_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    location_id = db.Column(db.String, db.ForeignKey('location.location_id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)

    def serialize(self):
        return {
            'product_quantity_id': self.product_quantity_id,
            'product_id': self.product_id,
            'location_id': self.location_id,
            'quantity': self.quantity
        }

class ProductMovement(db.Model):
    product_movement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String, db.ForeignKey('product.product_id'), nullable=False)
    from_location_id = db.Column(db.String, nullable=True)
    to_location_id = db.Column(db.String, nullable=True)
    qty = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            'product_movement_id': self.product_movement_id,
            'product_id': self.product_id,
            'from_location_id': self.from_location_id,
            'to_location_id': self.to_location_id,
            'qty': self.qty,
            'timestamp' : self.timestamp
        }
