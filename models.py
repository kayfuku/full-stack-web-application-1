from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime

db = SQLAlchemy()

def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(Integer, primary_key=True)
  name = db.Column(String())
  city = db.Column(String(120))
  state = db.Column(String(120))
  address = db.Column(String(120))
  phone = db.Column(String(120))
  image_link = db.Column(String(500))
  facebook_link = db.Column(String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  seeking_talent = db.Column(Boolean, default=False)
  seeking_description = db.Column(String(500), default='')
  website = db.Column(String(120))
  genres = db.Column(ARRAY(String))
  show = db.relationship('Show', backref=db.backref('venue', lazy=True))

  def __init__(self, name, city, state, address, phone, image_link, facebook_link, website, genres, 
                 seeking_talent=False, seeking_description=''):
    self.name = name
    self.city = city
    self.state = state
    self.address = address
    self.phone = phone
    self.image_link = image_link
    self.facebook_link = facebook_link
    self.seeking_description = seeking_description
    self.website = website
    self.genres = genres

  def __repr__(self):
    return '<Venue %r>' % self
  
  @property
  def serialize(self):
    return {'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'address': self.address,
            'phone': self.phone,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description, 
            'website': self.website,
            'genres': self.genres
            }
    
  
class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(Integer, primary_key=True)
  name = db.Column(String)
  city = db.Column(String(120))
  state = db.Column(String(120))
  phone = db.Column(String(120))
  genres = db.Column(String(120))
  image_link = db.Column(String(500))
  facebook_link = db.Column(String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  seeking_venue = db.Column(Boolean, default=False)
  seeking_description = db.Column(String(500), default='')
  website = db.Column(String(120))
  show = db.relationship('Show', backref=db.backref('artist', lazy=True))

  def __init__(self, name, city, state, phone, genres, image_link, facebook_link, website, 
                 seeking_venue=False, seeking_description=""):
    self.name = name
    self.city = city
    self.state = state
    self.phone = phone
    self.genres = genres
    self.image_link = image_link
    self.facebook_link = facebook_link
    self.seeking_description = seeking_description
    self.website = website

  def __repr__(self):
    return '<Artist %r>' % self

  @property
  def serialize(self):
    return {'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'genres': self.genres,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'seeking_description': self.seeking_description,
            'website': self.website
            }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(Integer, primary_key=True)
  venue_id = db.Column(Integer, ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(Integer, ForeignKey(Artist.id), nullable=False)
  start_time = db.Column(DateTime)

  def __init__(self, start_time):
    self.start_time = start_time

  def __repr__(self):
    return '<Show %r>' % self









