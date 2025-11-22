from datetime import datetime, timezone

from bs4 import BeautifulSoup

from .extensions import db


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

    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

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


class ApiKey(BaseDbModel, db.Model):
    __tablename__ = "ApiKey"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.String)

    def __init__(self, key, description=None):
        self.key = key
        self.description = description
