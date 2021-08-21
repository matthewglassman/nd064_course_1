import sqlite3
import os
import logging

from collections import defaultdict

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

#Set up logging

#Set loglevel to an Environment Variable
loglevel = os.getenv("UDACITY_APP_LOGLEVEL", "DEBUG").upper()

#Set logging output type dynamically depending on loglevel condition
loglevel = (
    getattr(logging, loglevel)
    if loglevel in ["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"]
    else logging.DEBUG
    )

#Create handlers to determine which logging goes to stdout and stderr
#Assign Logging Stream Handler for redirection to stdout
standard_out = logging.StreamHandler(sys.stout)

#Set the lowest threshold that gets set to stdout
standard_out = setLevel(loglevel)


#Global variable to hold number of times a db connection has been made.
db_connection_counter = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
  #Global variable to hold number of times a db connection has been made.
    global db_connection_counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_counter += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

#Create variable for return response status of 200 for healthz route
health = {'result': 'OK - healthy'}

#Define healthz endpoint
@app.route('/healthz', methods=['GET'])
def healthstatus():
  response = app.response_class(response = json.dumps(health), status=200, mimetype='application/json')

  return response

#Create mock data to test metrics endpoint
database_use = {'data':{'DatabaseQueries': 15, 'Posts': 4}}

#Define metrics endpoint
@app.route('/metrics', methods=['GET'])
def usage():
  connection = get_db_connection()
  posts = connection.execute('SELECT * FROM posts').fetchall()
  connection.close()
  response = app.response_class(response = json.dumps({'data':{"Database_Connections": db_connection_counter, "number_of_posts": len(posts)}}), status = 200, mimetype = 'application/json')

  return response

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
