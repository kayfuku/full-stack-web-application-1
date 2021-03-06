#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
# $ conda activate flask_env

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, abort, flash, redirect, url_for, jsonify
from flask_moment import Moment
from models import db_setup, Venue, Artist, Show
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime
import traceback
import sys


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

# TODO: connect to a local postgresql database
db = db_setup(app)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

# I like this filter helper, especially when you used it at the show page.
# It makes it user interactivity interesting. Well done! 😄
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # data=[{
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "venues": [{
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "num_upcoming_shows": 0,
    #   }, {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "num_upcoming_shows": 1,
    #   }]
    # }, {
    #   "city": "New York",
    #   "state": "NY",
    #   "venues": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }]

    data = []
    # This is like a view.
    upcoming_shows_rows = Show.query.filter(
        Show.start_time > datetime.datetime.now())

    areas = Venue.query.distinct(Venue.city, Venue.state).all()
    for area in areas:
        city_state = dict()
        city_state['city'] = area.city
        city_state['state'] = area.state

        city_state['venues'] = []
        venues = Venue.query.filter_by(city=area.city, state=area.state).all()
        for venue in venues:
            venue_dict = dict()
            venue_dict['id'] = venue.id
            venue_dict['name'] = venue.name

            # We can query on the view.
            num_upcoming_shows = upcoming_shows_rows \
                .filter(Show.venue_id == venue.id) \
                .count()
            venue_dict['num_upcoming_shows'] = num_upcoming_shows

            city_state['venues'].append(venue_dict)

        data.append(city_state)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "num_upcoming_shows": 0,
    #   }]
    # }

    search_term = request.form.get('search_term', None)
    venues = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()
    upcoming_shows_rows = Show.query.filter(
        Show.start_time > datetime.datetime.now())

    response = dict()
    response['data'] = []
    for v in venues:
        v_dict = v.get_dict
        response['count'] = len(venues)
        v_dict['num_upcoming_shows'] = upcoming_shows_rows.filter(
            Show.venue_id == v.id).count()
        response['data'].append(v_dict)

    return render_template(
        'pages/search_venues.html', results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # data1={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "past_shows": [{
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "genres": ["Classical", "R&B", "Hip-Hop"],
    #   "address": "335 Delancey Street",
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "914-003-1132",
    #   "website": "https://www.theduelingpianos.com",
    #   "facebook_link": "https://www.facebook.com/theduelingpianos",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 3,
    #   "name": "Park Square Live Music & Coffee",
    #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #   "address": "34 Whiskey Moore Ave",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "415-000-1234",
    #   "website": "https://www.parksquarelivemusicandcoffee.com",
    #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #   "seeking_talent": False,
    #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #   "past_shows": [{
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [{
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

    venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
    data = venue.get_dict

    # past_shows
    past_shows = Show.query.filter(
        Show.start_time <= datetime.datetime.now(),
        Show.venue_id == venue_id).all()
    data['past_shows'] = []
    for ps in past_shows:
        a = Artist.query.get(ps.artist_id)
        data['past_shows'].append({
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": ps.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    data['past_shows_count'] = len(past_shows)

    # upcoming_shows
    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.datetime.now(),
        Show.venue_id == venue_id).all()
    data['upcoming_shows'] = []
    for us in upcoming_shows:
        a = Artist.query.get(us.artist_id)
        data['upcoming_shows'].append({
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link,
            "start_time": us.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        new_venue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_talent=request.form['seeking_talent'],
            seeking_description=request.form['seeking_description'],
            website=request.form['website'],
            genres=request.form.getlist('genres')
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        print('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception as ex:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash(
            'An error occurred. Venue ' + request.form['name'] +
            ' could not be listed.')
        db.session.rollback()
        traceback.print_exc()

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    success = False
    try:
        # This returns BaseQuery. By using this, not sure how to print the venue name later.
        # venue_to_delete = Venue.query.filter_by(id=venue_id)
        # This returns Venue.
        venue_to_delete = Venue.query.filter_by(id=venue_id).one()
        print('test', type(venue_to_delete))
        db.session.delete(venue_to_delete)
        db.session.commit()
        flash('Venue {0} has been deleted successfully.'.format(
            venue_to_delete.name
        ))
        # This helps!
        print(sys.exc_info())
        print('Venue {0} (id: {1}) has been deleted.'.format(
            venue_to_delete.name, venue_to_delete.id))
        success = True
    except:
        db.session.rollback()
        flash('An error occurred. Venue {0} could not be deleted.'.format(
            venue_to_delete.name
        ))
        # This helps!
        print(sys.exc_info())
        print('Venue {0} (id: {1}) could not be deleted.'.format(
            venue_to_delete.name, venue_to_delete.id))
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    return jsonify({'success': success})
    # return None


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    # data=[{
    #   "id": 4,
    #   "name": "Guns N Petals",
    # }, {
    #   "id": 5,
    #   "name": "Matt Quevedo",
    # }, {
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    # }]

    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    # response={
    #   "count": 1,
    #   "data": [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "num_upcoming_shows": 0,
    #   }]
    # }

    search_term = request.form.get('search_term', None)
    artists = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()
    upcoming_shows_rows = Show.query.filter(
        Show.start_time > datetime.datetime.now())

    response = dict()
    response['data'] = []
    for a in artists:
        a_dict = a.get_dict
        response['count'] = len(artists)
        a_dict['num_upcoming_shows'] = upcoming_shows_rows.filter(
            Show.artist_id == a.id).count()
        response['data'].append(a_dict)

    return render_template(
        'pages/search_artists.html', results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    # data1={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "past_shows": [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data2={
    #   "id": 5,
    #   "name": "Matt Quevedo",
    #   "genres": ["Jazz"],
    #   "city": "New York",
    #   "state": "NY",
    #   "phone": "300-400-5000",
    #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "past_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    #   }],
    #   "upcoming_shows": [],
    #   "past_shows_count": 1,
    #   "upcoming_shows_count": 0,
    # }
    # data3={
    #   "id": 6,
    #   "name": "The Wild Sax Band",
    #   "genres": ["Jazz", "Classical"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "432-325-5432",
    #   "seeking_venue": False,
    #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "past_shows": [],
    #   "upcoming_shows": [{
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    #   }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    #   }],
    #   "past_shows_count": 0,
    #   "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]

    artist = Artist.query.filter(Artist.id == artist_id).one_or_none()
    data = artist.get_dict

    # past_shows
    past_shows = Show.query.filter(
        Show.start_time <= datetime.datetime.now(),
        Show.artist_id == artist_id).all()
    data['past_shows'] = []
    for ps in past_shows:
        v = Venue.query.get(ps.venue_id)
        data['past_shows'].append({
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": v.image_link,
            "start_time": ps.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    data['past_shows_count'] = len(past_shows)

    # upcoming_shows
    upcoming_shows = Show.query.filter(
        Show.start_time > datetime.datetime.now(),
        Show.artist_id == artist_id).all()
    data['upcoming_shows'] = []
    for us in upcoming_shows:
        v = Venue.query.get(us.venue_id)
        data['upcoming_shows'].append({
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": v.image_link,
            "start_time": us.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    data['upcoming_shows_count'] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # artist={
    #   "id": 4,
    #   "name": "Guns N Petals",
    #   "genres": ["Rock n Roll"],
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "326-123-5000",
    #   "website": "https://www.gunsnpetalsband.com",
    #   "facebook_link": "https://www.facebook.com/GunsNPetals",
    #   "seeking_venue": True,
    #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }

    # TODO: populate form with fields from artist with ID <artist_id>
    artist_to_update = Artist.query.get(artist_id)
    if artist_to_update is None:
        abort(404)

    artist = artist_to_update.get_dict
    form = ArtistForm(data=artist)

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    print('id: {}, genres: {}'.format(
        artist_id, ','.join(request.form.getlist('genres'))))
    if 'seeking_venue' in request.form:
        print('seeking_venue: {}'.format(request.form['seeking_venue']))

    try:
        seeking_venue = False
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'

        print(type(seeking_venue))

        new_artist = Artist.query.get(artist_id)

        new_artist.name = request.form['name']
        new_artist.city = request.form['city']
        new_artist.state = request.form['state']
        new_artist.phone = request.form['phone']
        new_artist.image_link = request.form['image_link']
        new_artist.facebook_link = request.form['facebook_link']
        new_artist.seeking_venue = seeking_venue
        new_artist.seeking_description = request.form['seeking_description']
        new_artist.website = request.form['website']
        new_artist.genres = ','.join(request.form.getlist('genres'))

        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
        print('Artist ' + request.form['name'] + ' was successfully edited!')

    except Exception as ex:
        flash(
            'An error occurred. Artist ' + request.form['name'] +
            ' could not be edited.')
        print(
            'An error occurred. Artist ' + request.form['name'] +
            ' could not be edited.')
        db.session.rollback()
        traceback.print_exc()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # venue={
    #   "id": 1,
    #   "name": "The Musical Hop",
    #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #   "address": "1015 Folsom Street",
    #   "city": "San Francisco",
    #   "state": "CA",
    #   "phone": "123-123-1234",
    #   "website": "https://www.themusicalhop.com",
    #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #   "seeking_talent": True,
    #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }

    # TODO: populate form with values from venue with ID <venue_id>
    venue_to_update = Venue.query.get(venue_id)
    if venue_to_update is None:
        abort(404)

    venue = venue_to_update.get_dict
    form = VenueForm(data=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        seeking_talent = False
        if 'seeking_talent' in request.form:
            seeking_talent = request.form['seeking_talent'] == 'y'

        new_venue = Venue.query.get(venue_id)

        new_venue.name = request.form['name']
        new_venue.city = request.form['city']
        new_venue.state = request.form['state']
        new_venue.phone = request.form['phone']
        new_venue.image_link = request.form['image_link']
        new_venue.facebook_link = request.form['facebook_link']
        new_venue.seeking_talent = seeking_talent
        new_venue.seeking_description = request.form['seeking_description']
        new_venue.website = request.form['website']
        new_venue.genres = request.form.getlist('genres')

        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
        print('Venue ' + request.form['name'] + ' was successfully edited!')

    except Exception as ex:
        flash(
            'An error occurred. Venue ' + request.form['name'] +
            ' could not be edited.')
        print(
            'An error occurred. Venue ' + request.form['name'] +
            ' could not be edited.')
        db.session.rollback()
        traceback.print_exc()

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # print('image_link:', request.form['image_link'])
    # print('seeking_venue:', request.form['seeking_venue'])

    try:
        seeking_venue = False
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'

        new_artist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=seeking_venue,
            seeking_description=request.form['seeking_description'],
            website=request.form['website'],
            genres=','.join(request.form.getlist('genres'))
        )
        db.session.add(new_artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        print('Artist ' + request.form['name'] + ' was successfully listed!')

    except Exception as ex:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash(
            'An error occurred. Artist ' + request.form['name'] +
            ' could not be listed.')
        print(
            'An error occurred. Artist ' + request.form['name'] +
            ' could not be listed.')
        db.session.rollback()
        traceback.print_exc()

    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # data=[{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "artist_id": 4,
    #   "artist_name": "Guns N Petals",
    #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 5,
    #   "artist_name": "Matt Quevedo",
    #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #   "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #   "venue_id": 3,
    #   "venue_name": "Park Square Live Music & Coffee",
    #   "artist_id": 6,
    #   "artist_name": "The Wild Sax Band",
    #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #   "start_time": "2035-04-15T20:00:00.000Z"
    # }]

    data = []
    shows = Show.query.all()
    for show in shows:
        s_dict = show.get_dict
        s_dict['venue_name'] = Venue.query.get(show.venue_id).name
        a = Artist.query.get(show.artist_id)
        s_dict['artist_name'] = a.name
        s_dict['artist_image_link'] = a.image_link
        data.append(s_dict)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    try:
        new_show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time']
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        print('Show was successfully listed!')

    except Exception as ex:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occurred. Show could not be listed.')
        print('An error occurred. Show could not be listed.')
        db.session.rollback()
        traceback.print_exc()

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
