from datetime import datetime

from bs4 import BeautifulSoup

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


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
    __tablename__ = "Document"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String)
    outline = db.Column(db.String)
    body = db.Column(db.String)

    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, body):
        self.body = body
        self._extract_title_and_outline()

    def _extract_title_and_outline(self):
        soup = BeautifulSoup(self.body, "html.parser")

        # Extract title
        title = soup.title.text if soup.title else ""

        # Extract outline
        outline = ""
        p_tags = soup.find_all("p")
        if p_tags:
            outline = p_tags[0].text
        else:
            div_tags = soup.find_all("div")
            if div_tags:
                outline = div_tags[0].text

        self.title = title
        self.outline = outline


class Index(BaseDbModel, db.Model):
    __tablename__ = "Index"

    id = db.Column(db.Integer, primary_key=True)

    index = db.Column(db.String)

    def __init__(self, index):
        self.index = index
