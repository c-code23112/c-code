from flask import Flask, make_response,send_from_directory,render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
from sqlalchemy.dialects import mysql
from sqlalchemy import create_engine


app = Flask(__name__)


app.secret_key = 'your_secret_key'


app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://root:123456@localhost/course_design_system'
app.config['SQLALCHchemy_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

cur = engine.raw_connection().cursor()
cur.execute("SELECT topic_id, topic_name FROM topics")
topics = cur.fetchall()
cur.close()
print(topics)