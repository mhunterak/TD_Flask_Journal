# --------------------------------
# Python Web Development Techdegree
# Project 5 - Flask Journal
# by Maxwell Hunter
# follow me on GitHub @mHunterAK
# --------------------------------

import controllers
import models

import datetime

from flask import Flask
from flask import render_template

app = Flask(__name__, static_url_path='/static')

##########
# VIEWS #
##########


def render_view(page, **kwargs):
    return render_template(
        page,
        copyright='Maxwell Hunter 2018',
        last_update=datetime.datetime.now(),
        **kwargs
    )

@app.route('/')
def index():
    return render_view('index.html')


# TODO Title should be hyperlinked to the detail page for each journal entry.
# TODO Include a link to add an entry.
# TODO Create 'details' view with the route '/details'
# TODO displaying the journal entry with all fields:
# TODO Title,
# TODO Date,
# TODO Time Spent,
# TODO What You Learned,
# TODO Resources to Remember.
# TODO Include a link to edit the entry.
# TODO Create 'add/edit' view with the route '/entry' that allows the user to
# TODO      add or edit journal entry with the following fields:
# TODO         Title,
# TODO         Date,
# TODO         Time Spent,
# TODO         What You Learned,
# TODO         Resources to Remember.

if __name__ == '__main__':
    app.run(debug=models.DEBUG, port=8000)
