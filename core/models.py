from . import db


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    is_active = db.Column(db.Boolean(), default=False)
    
    def __repr__(self):
        return '<Product %r>' % self.sku


class Progress(db.Model):
    __tablename__ = 'progresses'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(255), unique=True, index=True, nullable=False)
    done = db.Column(db.Integer)
    pending = db.Column(db.Integer)
    total = db.Column(db.Integer)
