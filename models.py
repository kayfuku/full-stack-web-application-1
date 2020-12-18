from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
  description = db.Column(String(500), default='')
  website = db.Column(String(120))
  genres = db.Column(ARRAY(String))
  show = db.relationship('Show', backref=db.backref('venue', lazy=True))

  
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
  description = db.Column(String(500), default='')
  website = db.Column(String(120))
  show = db.relationship('Show', backref=db.backref('artist', lazy=True))


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(Integer, primary_key=True)
  venue_id = db.Column(Integer, ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(Integer, ForeignKey(Artist.id), nullable=False)
  start_time = db.Column(String(), nullable=False)









