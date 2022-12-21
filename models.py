from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BaseDbModel:
    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Document(BaseDbModel, db.Model):
    __tablename__ = 'Document'

    id = db.Column(db.Integer, primary_key=True)
    
    body = db.Column(db.String)

    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, body):
        self.body = body

    def format(self):
        return {
            'id': self.id,
            'body': self.body,
        }        
        
class Index(BaseDbModel, db.Model):
    __tablename__ = 'Index'

    id = db.Column(db.Integer, primary_key=True)
    
    index = db.Column(db.String)
    
    def __init__(self, index):
        self.tmdb_id = index
