#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="venue")


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref="artist")


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
                'Artist.id'), nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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

  all_cities = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []

  for area in all_cities:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venue_data
    })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term=request.form.get('search_term', '')
  search_found = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data=[]

  for find in search_found:
    data.append({
      "id": find.id,
      "name": find.name
    })

    response = {
      "count": len(search_found),
      "data": data
      }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

 venue = Venue.query.filter_by(id=venue_id).first()

 upcoming_show_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id,Show.start_time >= datetime.now()).all()
 past_show_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id,Show.start_time < datetime.now()).all()

 upcoming_shows = []

 for show in upcoming_show_list:
    upcoming_shows.append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      })

 past_shows = []

 for show in past_show_list:
    past_shows.append({
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      })

 data = {
   "id": venue.id,
   "name": venue.name,
   "genres": [{
     "genre" : venue.genres
   }],
   "address": venue.address,
   "city": venue.city,
   "state": venue.state,
   "phone": venue.phone,
   "website": venue.website,
   "facebook_link": venue.facebook_link,
   "seeking_talent": venue.seeking_talent,
   "seeking_description": venue.seeking_description,
   "image_link": venue.image_link,
   "past_shows": past_shows,
   "upcoming_shows": upcoming_shows,
   "past_shows_count": len(past_shows),
   "upcoming_shows_count": len(upcoming_shows),
 }

 return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False
  try:
    venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    facebook_link = request.form.get('facebook_link'),
    )
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
       # unsuccesful
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  else:
       # successful
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  all_artists = Artist.query.all()
  data = []

  for artist in all_artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term=request.form.get('search_term', '')
  search_found = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data=[]

  for find in search_found:
    data.append({
      "id": find.id,
      "name": find.name
    })

    response = {
      "count": len(search_found),
      "data": data
      }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first()

  upcoming_show_list = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id,Show.start_time >= datetime.now()).all()
  past_show_list = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id,Show.start_time < datetime.now()).all()

  upcoming_shows = []

  for show in upcoming_show_list:
     upcoming_shows.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      })

  past_shows = []

  for show in past_show_list:
     past_shows.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      })

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [{
      "genre" : artist.genres
    }],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False
  try:
    artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    genres = request.form.getlist('genres'),
    facebook_link = request.form.get('facebook_link'),
    )
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
       # unsuccesful
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
       # successful
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  allShows = db.session.query(Show).join(Artist).join(Venue).filter(Show.start_time >= datetime.now()).all()

  data = []

  for show in allShows:
     data.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  # TO FINISH ... copied from Artist ... incomplete
  # error = False
  # try:
  #   show = Show(
  #   name = request.form['name'],
  #   city = request.form['city'],
  #   state = request.form['state'],
  #   phone = request.form['phone'],
  #   genres = request.form.getlist('genres'),
  #   facebook_link = request.form.get('facebook_link'),
  #   )
  #   db.session.add(artist)
  #   db.session.commit()
  # except Exception as e:
  #   error = True
  #   db.session.rollback()
  # finally:
  #   db.session.close()
  # if error:
  #      # unsuccesful
  #   flash('An error occurred. Show named ... ' + data.name + ' could not be listed.')
  # else:
  #      # successful
  #   flash('Artist ' + request.form['name'] + ' was successfully listed!')
  #
  #   return render_template('pages/home.html')


  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
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
