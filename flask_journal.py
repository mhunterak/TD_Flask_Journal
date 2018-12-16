# --------------------------------
# Python Web Development Techdegree
# Project 5 - Flask Journal
# by Maxwell Hunter
# follow me on GitHub @mHunterAK
# --------------------------------

# After you’ve created a Flask project,
# added all the required dependencies,
from flask import Flask
''' future imports
from peewee import (Model, SqliteDatabase,
                    DateField, DateTimeField, TextField, IntegerField
                    )  # pragma: no cover
import datetime
import os
import re
'''

# setup your project structure
app = Flask(__name__, static_url_path='/static')
DEBUG = True

# MODEL #
# TODO: create a Peewee model class for journal entries.
# TODO: Add the ability to delete a journal entry.

# VIEW #
# TODO Title should be hyperlinked to the detail page for each journal entry.
# TODO Include a link to add an entry.
# TODO Create “details” view with the route “/details”
# TODO displayingthe journal entry with all fields:
# TODO Title,
# TODO Date,
# TODO Time Spent,
# TODO What You Learned,
# TODO Resources to Remember.
# TODO Include a link to edit the entry.
# TODO Create “add/edit” view with the route “/entry” that allows the user to
# TODO      add or edit journal entry with the following fields:
# TODO         Title,
# TODO         Date,
# TODO         Time Spent,
# TODO         What You Learned,
# TODO         Resources to Remember.

# CONTROLLER #
# TODO Add necessary routes for the application:
# TODO     /’
# TODO     /entries
# TODO     /entries/<slug>
# TODO     /entries/edit/<slug>
# TODO     /entries/delete/<slug>/entry
# TODO Create “list” view using the route /entries.
# TODO The list view contains:
# TODO     a list of journal entries,
# TODO     which displays
# TODO     Title and Date for Entry.
# TODO Add the ability to delete a journal entry.


# EXTRA CREDIT *
# TODO XC: Add tags to journal entries in the model.
# TODO XC: Add tags to journal entries on the listing page
# TODO allow the tags to be links to a list of specific tags.
# TODO XC: Add tags to the details page.
# TODO XC: Create password protection or user login.
# TODO XC: provide credentials for code review.
# TODO XC: Routing uses slugs.

# GENERAL *
# TODO Make sure your coding style complies with PEP 8.
# TODO check off all of the items on the Student Project Submission Checklist.

if __name__ == '__main__':
    if DEBUG:
        pass
    else:
        pass
    app.run(debug=DEBUG)
