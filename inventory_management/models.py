from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to movements
    movements = db.relationship('ProductMovement', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.product_id}: {self.name}>'

class Location(db.Model):
    __tablename__ = 'locations'
    
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    manager = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships to movements
    movements_from = db.relationship('ProductMovement', 
                                   foreign_keys='ProductMovement.from_location',
                                   backref='from_location_obj', lazy=True)
    movements_to = db.relationship('ProductMovement', 
                                 foreign_keys='ProductMovement.to_location',
                                 backref='to_location_obj', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.location_id}: {self.name}>'

class ProductMovement(db.Model):
    __tablename__ = 'product_movements'
    
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('locations.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('locations.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Movement {self.movement_id}: {self.qty} x {self.product_id}>'
    
    @property
    def movement_type(self):
        """Determine the type of movement"""
        if self.from_location and self.to_location:
            return "Transfer"
        elif self.to_location and not self.from_location:
            return "Stock In"
        elif self.from_location and not self.to_location:
            return "Stock Out"
        else:
            return "Unknown"
