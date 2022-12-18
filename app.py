import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Artist, Venue, Show
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  distinct_venues_by_cities = Venue.query.distinct(Venue.city).all()
  data = []
  for city in distinct_venues_by_cities:
    venues_by_city = Venue.query.filter_by(city=city.city)
    venues = []
    for venue in venues_by_city:
      venues.append({
        "id": venue.id,
        "name": venue.name
      })
    data.append({
      "city": venues_by_city[0].city,
      "state": venues_by_city[0].state,
      "venues": venues
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.like(search)).all()
  except:
    flash('Error!')

  response = {
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  data = Venue.query.get(venue_id)
  data.genres = json.loads(data.genres)
  upcoming_shows = Show.query.filter_by(venue_id=venue_id).where(
      Show.start_time > str(datetime.now())).all()
  past_shows = Show.query.filter_by(venue_id=venue_id).where(
      Show.start_time < str(datetime.now())).all()
  upcoming_shows_count = Show.query.filter_by(venue_id=venue_id).where(
      Show.start_time > str(datetime.now())).count()
  past_shows_count = Show.query.filter_by(venue_id=venue_id).where(
      Show.start_time < str(datetime.now())).count()

  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = upcoming_shows_count
  data.past_shows = past_shows
  data.past_shows_count = past_shows_count
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
  body = {}
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = json.dumps(request.form.getlist('genres'))
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    if request.form.get('seeking_talent') == 'y':
      seeking_talent = True
    else:
      seeking_talent = False
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()

    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['genres'] = venue.genres
    body['image_link'] = venue.image_link
    body['facebook_link'] = venue.facebook_link
    body['website_link'] = venue.website_link
    body['seeking_talent'] = venue.seeking_talent
    body['seeking_description'] = venue.seeking_description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # return redirect(url_for('venues'))
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(500)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    for show in venue.shows:
      db.session.delete(show)    
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
     return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    search_term = request.form.get('search_term', '')
    search = "%{}%".format(search_term)
    artists = Artist.query.filter(Artist.name.like(search)).all()
  except:
    flash('Error!')
  response={
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # data = Artist.query.get(artist_id)
  # data.shows = Show.query.filter_by(artist_id=artist_id).all()
  data = Artist.query.get(artist_id)
  data.genres = json.loads(data.genres)
  upcoming_shows = Show.query.filter_by(artist_id=artist_id).where(
      Show.start_time > str(datetime.now())).all()
  past_shows = Show.query.filter_by(artist_id=artist_id).where(
      Show.start_time < str(datetime.now())).all()
  upcoming_shows_count = Show.query.filter_by(artist_id=artist_id).where(
      Show.start_time > str(datetime.now())).count()
  past_shows_count = Show.query.filter_by(artist_id=artist_id).where(
      Show.start_time < str(datetime.now())).count()
 
  data.upcoming_shows = upcoming_shows
  data.upcoming_shows_count = upcoming_shows_count
  data.past_shows = past_shows
  data.past_shows_count = past_shows_count
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  if artist.seeking_venue:
    form.seeking_venue = artist.seeking_venue 
  if artist.seeking_description:
    form.seeking_description = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  error = False
  body = {}
  try:
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = json.dumps(request.form.getlist('genres'))
    artist.image_link = request.form.get('image_link', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website_link = request.form.get('website_link', '')
    if request.form.get('seeking_venue') == 'y':
      artist.seeking_venue = True
    else:
      artist.seeking_venue = False
    artist.seeking_description = request.form.get('seeking_description')
    db.session.add(artist)
    db.session.commit()

    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['genres'] = artist.genres
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['website_link'] = artist.website_link
    body['seeking_venue'] = artist.seeking_talent
    body['seeking_description'] = artist.seeking_description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # return redirect(url_for('venues'))
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')
    abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  error = False
  body = {}
  try:
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = json.dumps(request.form.getlist('genres'))
    venue.image_link = request.form.get('image_link', '')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website_link = request.form.get('website_link', '')
    if request.form.get('seeking_talent') == 'y':
      venue.seeking_talent = True
    else:
      venue.seeking_talent = False
    venue.seeking_description = request.form.get('seeking_description')
    db.session.add(venue)
    db.session.commit()

    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['genres'] = venue.genres
    body['image_link'] = venue.image_link
    body['facebook_link'] = venue.facebook_link
    body['website_link'] = venue.website_link
    body['seeking_talent'] = venue.seeking_talent
    body['seeking_description'] = venue.seeking_description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # return redirect(url_for('venues'))
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('An error occurred. Venue ' +
          request.form['name'] + ' could not be listed.')
    abort(500)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  body = {}
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = json.dumps(request.form.getlist('genres'))
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website_link = request.form.get('website_link', '')
    if request.form.get('seeking_venue') == 'y':
      seeking_venue = True
    else:
      seeking_venue = False
    seeking_description = request.form.get('seeking_description')
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
                  facebook_link=facebook_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()

    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['genres'] = artist.genres
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['website_link'] = artist.website_link
    body['seeking_venue'] = artist.seeking_venue
    body['seeking_description'] = artist.seeking_description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # return redirect(url_for('venues'))
    return render_template('pages/home.html')
  else:
    flash('An error occurred. Artist ' +
          request.form['name'] + ' could not be listed.')
    abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Show.query.all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  body = {}
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()

    body['artist_id'] = show.artist_id
    body['venue_id'] = show.venue_id
    body['started_at'] = show.start_time
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    flash('An error occurred while listing show!')

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
