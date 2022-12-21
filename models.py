from datetime import datetime
from random import randint

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from project.config import PROFILE_PICTURE_BASE_URL


db = SQLAlchemy()
migrate = Migrate()

class BaseDbModel:
    # TODO: log errors
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


class User(BaseDbModel, db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String)

    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    phone_number = db.Column(db.String)
    email = db.Column(db.String)

    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String)
    
    profile_picture = db.Column(db.String)

    followings = db.relationship('user_follows', backref='followings', foreign_keys='user_follows.follower')
    followers = db.relationship('user_follows', backref='followers', foreign_keys='user_follows.followed')
     
    watch_later = db.relationship('user_watch_later', backref='user', foreign_keys='user_watch_later.user_id')
    favourites = db.relationship('user_favourites', backref='user', foreign_keys='user_favourites.user_id')
    
    tickets = db.relationship('Ticket', backref='user', cascade="all, delete")

    movie_reviews = db.relationship('Movie_Review', backref='user', foreign_keys='Movie_Review.user_id')
    cinema_reviews = db.relationship('Cinema_Review', backref='user', foreign_keys='Cinema_Review.user_id')

    coupon_purchases = db.relationship('Coupon_Purchase', backref='user', foreign_keys='Coupon_Purchase.user_id')
    promo_code_uses = db.relationship('Promo_Code_Use', backref='user', foreign_keys='Promo_Code_Use.user_id')

    def __init__(self, first_name, last_name, phone_number, email, 
                 date_of_birth, gender, auth0_id, profile_picture=None):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.auth0_id = auth0_id
        self.profile_picture = profile_picture

    def insert(self):
        if self.profile_picture is None:
            avatar = randint(1, 9)
            self.profile_picture = f'avatars/{avatar}.jpg'

        self.email = self.email.lower()

        super().insert()

    def format(self):
        return {
            'id': self.id,
            'auth0_id': self.auth0_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile_picture': f'{PROFILE_PICTURE_BASE_URL}{self.profile_picture}',
            'phone_number': self.phone_number,
            'email': self.email,
            'date_of_birth': self.date_of_birth.strftime("%Y-%m-%d") if self.date_of_birth else None,
            'gender': self.gender
        }


class user_follows(BaseDbModel, db.Model):
    __tablename__ = 'user_follows'
    
    id = db.Column(db.Integer, primary_key=True)
    
    follower = db.Column(db.Integer, db.ForeignKey('User.id'))
    followed = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    def __init__(self, follower, followed):
        self.follower = follower
        self.followed = followed
        
        
class Movie(BaseDbModel, db.Model):
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True)
    
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False, index=True)
    imdb_id = db.Column(db.String)
    
    title = db.Column(db.String)
    original_title = db.Column(db.String)
    original_language = db.Column(db.String)
    
    tagline = db.Column(db.String)
    overview = db.Column(db.String)
    
    status = db.Column(db.String)
    adult = db.Column(db.Boolean)
    
    release_date = db.Column(db.Date)
    runtime = db.Column(db.Integer)
    
    poster_url = db.Column(db.String)
    backdrop_url = db.Column(db.String)
    
    budget = db.Column(db.Integer)
    
    movie_reviews = db.relationship('Movie_Review', backref='movie', foreign_keys='Movie_Review.movie_id')
    genres = db.relationship('Movie_Genre', backref='movie', foreign_keys='Movie_Genre.movie_id')

    def __init__(self, tmdb_id, imdb_id, title, original_title, original_language, tagline, 
                 overview, status, adult, release_date, runtime, poster_url, backdrop_url, budget):
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.title = title
        self.original_title = original_title
        self.original_language = original_language
        self.tagline = tagline
        self.overview = overview
        self.status = status
        self.adult = adult
        self.release_date = release_date
        self.runtime = runtime
        self.poster_url = poster_url
        self.backdrop_url = backdrop_url
        self.budget = budget

    def format(self):
        return {
            'id': self.id,
            'tmdb_id': self.tmdb_id,
            'imdb_id': self.imdb_id,
            'title': self.title,
            'original_title': self.original_title,
            'original_language': self.original_language,
            'tagline': self.tagline,
            'overview': self.overview,
            'status': self.status,
            'adult': self.adult,
            'release_date': self.release_date.strftime("%Y-%m-%d"),
            'runtime': self.runtime,
            'poster_url': self.poster_url,
            'backdrop_url': self.backdrop_url,
            'budget': self.budget
        }


class user_watch_later(BaseDbModel, db.Model):
    __tablename__ = 'user_watch_later'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'))
    
    def __init__(self, user_id, movie_id):
        self.user_id = user_id
        self.movie_id = movie_id


class user_favourites(BaseDbModel, db.Model):
    __tablename__ = 'user_favourites'
    
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'))
    
    def __init__(self, user_id, movie_id):
        self.user_id = user_id
        self.movie_id = movie_id


class Genre(BaseDbModel, db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String)
    tmdb_id = db.Column(db.Integer)

    def __init__(self, name, tmdb_id):
        self.name = name
        self.tmdb_id = tmdb_id

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'tmdb_id': self.tmdb_id
        }
        
        
class Movie_Genre(BaseDbModel, db.Model):
    __tablename__ = 'Movie_Genre'

    id = db.Column(db.Integer, primary_key=True)
    
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('Genre.id'))

    def __init__(self, movie_id, genre_id):
        self.movie_id = movie_id
        self.genre_id = genre_id


class Movie_Review(BaseDbModel, db.Model):
    __tablename__ = 'Movie_Review'

    id = db.Column(db.Integer, primary_key=True)
    
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    is_spoiler = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    
    rating = db.Column(db.Integer)
    review = db.Column(db.String)
    
    def __init__(self, movie_id, user_id, is_spoiler, rating, review):
        self.movie_id = movie_id
        self.user_id = user_id
        self.is_spoiler = is_spoiler
        self.rating = rating
        self.review = review
        
    def insert(self):
        self.created_at = datetime.now()
        super().insert()

    def format(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'user_id': self.user_id,
            'is_spoiler': self.is_spoiler,
            'created_at': self.created_at, #.strftime("%Y-%m-%d %H:%M:%S")
            'rating': self.rating,
            'review': self.review
        }


class Ticket(BaseDbModel, db.Model):
    __tablename__ = 'Ticket'

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.relationship('User', backref='Ticket', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    price = db.Column(db.Float(precision=2))

    hall = db.Column(db.String)
    seat = db.Column(db.String)

    movie = db.Column(db.String)
    cinema_id = db.Column(db.Integer, db.ForeignKey('Cinema.id'))

    location = db.Column(db.String)
    qr_code = db.Column(db.String)

    inside = db.Column(db.Boolean)

    def __init__(self, user_id, hall, seat, movie, cinema_id, location, qr_code, inside, price):
        self.user_id = user_id
        self.hall = hall
        self.seat = seat
        self.movie = movie
        self.cinema_id = cinema_id
        self.location = location
        self.qr_code = qr_code
        self.inside = inside
        self.price = price

    def format(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hall': self.hall,
            'seat': self.seat,
            'movie': self.movie,
            'cinema_id': self.cinema_id,
            'location': self.location,
            'qr_code': self.qr_code,
            'inside': self.inside,
            'price': self.price
        }


class Promo_Code(BaseDbModel, db.Model):
    __tablename__ = 'Promo_Code'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True)

    discount = db.Column(db.Integer)

    code_uses = db.relationship('Promo_Code_Use', backref='promo_code', foreign_keys='Promo_Code_Use.promo_code_id', cascade="all, delete-orphan")

    def __init__(self, code, discount):
        self.code = code
        self.discount = discount

    def format(self):
        return {
            'id': self.id,
            'code': self.code,
            'discount': self.discount
        }
        
        
class Promo_Code_Use(BaseDbModel, db.Model):
    __tablename__ = 'Promo_Code_Use'

    id = db.Column(db.Integer, primary_key=True)
    
    promo_code_id = db.Column(db.Integer, db.ForeignKey('Promo_Code.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __init__(self, promo_code_id, user_id):
        self.promo_code_id = promo_code_id
        self.user_id = user_id



class Faq(BaseDbModel, db.Model):
    __tablename__ = 'Faq'

    id = db.Column(db.Integer, primary_key=True)
    
    question = db.Column(db.String, nullable=False)
    answer = db.Column(db.String)

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer
        }


class Cinema(BaseDbModel, db.Model):
    __tablename__ = 'Cinema'

    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String)
    adderss = db.Column(db.String)
    
    logo_url = db.Column(db.String)
    backdrop_url = db.Column(db.String)
    
    location_url = db.Column(db.String)
    
    about = db.Column(db.String)
    
    phone_number = db.Column(db.String)
    number_of_halls = db.Column(db.Integer)
    
    usher_redeem_password = db.Column(db.String)
    
    cinema_reviews = db.relationship('Cinema_Review', backref='cinema', foreign_keys='Cinema_Review.cinema_id')
    coupons = db.relationship('Coupon', backref='cinema', foreign_keys='Coupon.cinema_id')
    
    def __init__(self, name, adderss, logo_url, backdrop_url, 
                 location_url, about, phone_number, number_of_halls, 
                 usher_redeem_password):
        self.name = name
        self.adderss = adderss
        self.logo_url = logo_url
        self.backdrop_url = backdrop_url
        self.location_url = location_url
        self.about = about
        self.phone_number = phone_number
        self.number_of_halls = number_of_halls
        self.usher_redeem_password = usher_redeem_password
        
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'adderss': self.adderss,
            'logo_url': self.logo_url,
            'backdrop_url': self.backdrop_url,
            'location_url': self.location_url,
            'about': self.about,
            'phone_number': self.phone_number,
            'number_of_halls': self.number_of_halls
        }
        

class Cinema_Review(BaseDbModel, db.Model):
    __tablename__ = 'Cinema_Review'

    id = db.Column(db.Integer, primary_key=True)
    
    cinema_id = db.Column(db.Integer, db.ForeignKey('Cinema.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    rating = db.Column(db.Integer)
    review = db.Column(db.String)
    
    def __init__(self, cinema_id, user_id, rating, review):
        self.cinema_id = cinema_id
        self.user_id = user_id
        self.rating = rating
        self.review = review

    def format(self):
        return {
            'id': self.id,
            'cinema_id': self.cinema_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review': self.review
        }
        
        
class Scheduled_Movie(BaseDbModel, db.Model):
    __tablename__ = 'Scheduled_Movie'
    
    id = db.Column(db.Integer, primary_key=True)
    
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'))
    cinema_id = db.Column(db.Integer, db.ForeignKey('Cinema.id'))
 
    def __init__(self, movie_id, cinema_id):
        self.movie_id = movie_id
        self.cinema_id = cinema_id
        
    def format(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'cinema_id': self.cinema_id
        }
        

# TODO: check db.decimal vs db.float
class Coupon(BaseDbModel, db.Model):
    __tablename__ = 'Coupon'

    id = db.Column(db.Integer, primary_key=True)
    
    description = db.Column(db.String)
    ticket_type = db.Column(db.String)
    
    cinema_id = db.Column(db.Integer, db.ForeignKey('Cinema.id'))
    
    price = db.Column(db.Float(precision=2))
    original_price = db.Column(db.Float(precision=2), nullable=False)
    
    expiration_date = db.Column(db.DateTime)
    count = db.Column(db.Integer)
    
    purchases = db.relationship('Coupon_Purchase', backref='coupon', foreign_keys='Coupon_Purchase.coupon_id')
    
    def __init__(self, cinema_id, price, expiration_date, count, 
                 description, ticket_type, original_price):
        self.cinema_id = cinema_id
        self.price = price
        self.expiration_date = expiration_date
        self.count = count
        self.description = description
        self.ticket_type = ticket_type
        self.original_price = original_price
        
    def format(self):
        return {
            'id': self.id,
            'cinema_id': self.cinema_id,
            'price': self.price,
            'expiration_date': self.expiration_date.strftime("%Y-%m-%d") if self.expiration_date else None,
            'count': self.count,
            'description': self.description,
            'ticket_type': self.ticket_type,
            'original_price': self.original_price,
            'discount': round(100 * (self.original_price - self.price) / self.original_price, 2) if self.original_price else None
        }
        

class Coupon_Purchase(BaseDbModel, db.Model):
    __tablename__ = 'Coupon_Purchase'

    id = db.Column(db.Integer, primary_key=True)
    
    coupon_id = db.Column(db.Integer, db.ForeignKey('Coupon.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    amount_cents = db.Column(db.Float(precision=2))
    
    order_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    transaction_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    
    purchase_date = db.Column(db.DateTime)
    count = db.Column(db.Integer)
    
    is_paid = db.Column(db.Boolean, default=False)
    is_expired = db.Column(db.Boolean, default=False)
    
    coupon_uses = db.relationship('Coupon_Use', backref='coupon_purchase', foreign_keys='Coupon_Use.coupon_purchase_id')
    
    def __init__(self, coupon_id, user_id, is_paid, amount_cents, 
                 order_id, transaction_id, purchase_date, count):
        self.coupon_id = coupon_id
        self.user_id = user_id
        self.is_paid = is_paid
        self.amount_cents = amount_cents
        self.order_id = order_id
        self.transaction_id = transaction_id
        self.purchase_date = purchase_date
        self.count = count
        
    def format(self):
        return {
            'id': self.id,
            'coupon_id': self.coupon_id,
            'user_id': self.user_id,
            'is_paid': self.is_paid,
            'is_expired': self.is_expired,
            'amount_cents': self.amount_cents,
            'order_id': self.order_id,
            'transaction_id': self.transaction_id,
            'purchase_date': self.purchase_date,
            'count': self.count
        }
        
        
class Coupon_Use(BaseDbModel, db.Model):
    __tablename__ = 'Coupon_Use'

    id = db.Column(db.Integer, primary_key=True)
    
    coupon_purchase_id = db.Column(db.Integer, db.ForeignKey('Coupon_Purchase.id'))
    
    use_date = db.Column(db.DateTime)
    count = db.Column(db.Integer)
    
    is_used = db.Column(db.Boolean, default=False)
    
    def __init__(self, coupon_purchase_id, use_date, count):
        self.coupon_purchase_id = coupon_purchase_id
        self.use_date = use_date
        self.count = count
        
    def format(self):
        return {
            'id': self.id,
            'coupon_purchase_id': self.coupon_purchase_id,
            'use_date': self.use_date,
            'count': self.count,
            'is_used': self.is_used
        }
