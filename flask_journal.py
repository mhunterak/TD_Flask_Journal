# --------------------------------
# Python Web Development Techdegree
# Project 5 - Flask Journal
# by Maxwell Hunter
# follow me on GitHub @mHunterAK
#
# I am aiming for the
# Exceeds Expectations grade on this project!
# --------------------------------

# models holds the object blueprints, and method for initializing the database
from models import (
    DEBUG,  # Global variables
    Entry, User, Tag,  # Model objects
    initialize  # functions
)

from datetime import datetime as dt  # pragma: no cover
from random import choice as random_choice  # pragma: no cover
from re import sub  # pragma: no cover
from flask import (   # pragma: no cover
    Flask,
    request, flash,
    Markup, render_template, redirect, url_for
    )
from flask_bcrypt import check_password_hash  # pragma: no cover
from flask_login import (  # pragma: no cover
    LoginManager, login_required
)
app = Flask(__name__, static_url_path='/static')
key_choices = u'abcdefgh0123456789'
key = ''
for i in range(32):
    key += random_choice(key_choices)
app.secret_key = key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return User.get(User.id == userid)
    except User.DoesNotExist:
        return None

@app.route('/logout')
def logout():
    User.logout()
    flash("You've been logged out", 'success')
    return redirect(url_for('index'))

# ##### #
# VIEWS #
# ##### #
# this is the main script,
# because routing must occur in the same file as app


# this renders the template with default information that every template uses
def render_view(page, **kwargs):
    return render_template(
        page,
        copyright='2018 Maxwell Hunter',
        last_update='2018-12-20',
        **kwargs
    )

# TODONE XC: Create password protection or user login.
@app.route('/login', methods=('GET', 'POST'))
def login():
    # if the user is submitting a form
    if request.method == "POST":
        # see if they're redirected from another page
        # because they weren't logged in
        next = request.args.get('next')
        # try to log them in
        try:
            # get the user they're trying to log in as
            user=User.get(User.username == request.form['username'])
            # if their password is valid
            if check_password_hash(user.password, request.form['password']):
                # log them in
                User.login_user(
                    request.form['username'],
                    request.form['password'])
                # show login message
                flash('Log in successful, welcome back {}'.format(request.form['username']))
            else:
                # if the password is incorrect, tell them the user doesn't exist
                raise User.DoesNotExist
            # if there's another page to forward to after logging in
            if next:
                # forward them to that page
                return redirect(next)
            else:
                # if there's nowhere to forward to, send them to the index page
                return redirect(url_for('index'))
        # if the user is not found or password is incorrect
        except User.DoesNotExist:
            # tell them so
            flash("Username or password incorrect, please try again")
    # render the login form
    return render_view('login.html')
# TODONE XC: provide credentials for code review.
# SEE README.md

# TODONE Add ALL necessary routes for the application:
@app.route('/index.html')
# TODONE route for index
# TODONE necessary routes /
@app.route('/')
def index():
    # the index page looked like a list of entries to me,
    # so I moved index.html to /entries and had it forward
    return redirect(
        url_for('entry_list')
        )


# TODONE route for entries list
# TODONE necessary routes /entries
# TODONE Create 'list' view using the route /entries.
# TODONE Title should be hyperlinked to the detail page for each
#        journal entry.

@app.route('/entries')
@app.route('/entries/')
def entry_list():
    # TODONE The list view contains:
    entries = Entry.select()
    # TODONE     a list of journal entries,
    return render_view(
        # TODONE     which displays
        # TODONE          Title and Date for Entry.
        'index.html',
        entries=entries)


#  Include a link to add an entry
#      /entries/add
# TODONE necessary routes /entry # new entry
# TODONE? Create 'add/edit' view with the route


@app.route('/entry')
@app.route('/entries/add', methods=('GET', 'POST'))
@app.route('/entries/add/', methods=('GET', 'POST'))
@login_required
def add():
    # if the form is submitted
    if request.method == 'POST':
        # TODONE connect 'create_entry' class methed from Entry
        entry = Entry.create_entry(
            title=request.form['title'],
            date=request.form['date'],
            time_spent=request.form['timeSpent'],
            learned=request.form['whatILearned'],
            resources=request.form['ResourcesToRemember'],
        )
        # tell them the entry was created
        flash('Entry #{} created'.format(entry.id))
        # forward to the details page
        return redirect(url_for(
            'details_by_slug',
            slug=entry.slugify_title()))
    return render_view('new.html')


# ### Entry Details


# TODONE Create 'details' view with the route '/details'
# TODONE necessary routes /entries/<slug>
@app.route('/entries/<slug>')
@app.route('/entries/<slug>/details')
def details_by_slug(slug):
    # TODONE displaying the journal entry with all fields:
    entry = Entry.get_entry_from_slug(slug)
    # TODONE Title,
    # TODONE Date,
    # TODONE Time Spent,
    # TODONE What You Learned,
    # TODONE Resources to Remember.
    if entry is None:
        flash("no entry found")
    return render_view(
        'detail.html',
        Markup=Markup,
        entry=entry,
        slug=slug,
        )



# TODONE Include a link to edit the entry.
#      /entries/edit/<slug>
# TODONE necessary routes /entries/edit/<slug>
# TODONE     add or edit journal entry with the following fields:
@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit_entry(slug):
    # get the entry from slug
    entry = Entry.get_entry_from_slug(slug)
    # if the form is submitted
    if request.method == 'POST':
        # if the edit is successful
        if entry.edit(
            # TODONE Title,
            title=request.form['title'],
            # TODONE Date,
            date=request.form['date'],
            # TODONE Time Spent,
            time_spent=request.form['timeSpent'],
            # TODONE What You Learned,
            learned=request.form['whatILearned'],
            # TODONE Resources to Remember.
            resources=request.form['ResourcesToRemember'],
        ):
            flash('Entry #{} updated'.format(entry.id))
            # reload the entry
            entry = Entry.get(Entry.id == entry.id)
            slug = entry.slugify_title()
            # forward to detail page
            return redirect(url_for('details_by_slug', slug=slug))
    # on get 'GET' method (not 'POST')
    return render_view(
        'edit.html',
        entry=entry,
        slug=slug,)


# TODONE necessary routes /entries/delete/<slug>
@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
@login_required
def delete_entry(slug):
    # require 'POST' nethod to actually delete,
    entry = Entry.get_entry_from_slug(slug)
    if request.method == 'POST':
        if request.form['delete_confirm'].upper() == "DELETE":
            entryID = entry.id
            # also deletes related tags
            entry.delete_entry()
            flash("Entry #{} Deleted".format(entryID), 'success')
            return redirect(url_for('index'))
        else:
            flash('Please confirm deletion')
    return render_view(
        'delete.html',
        entry=entry,
    )

@app.route('/entries/<slug>/tag', methods=('GET', 'POST'))
@login_required
# add new tags
def tag_entry(slug):
    # get entry
    entry = Entry.get_entry_from_slug(slug)
    # if the form is submitted,
    if request.method == 'POST':
        # load the input text
        input = request.form['tags']
        # remove whitespace
        tagstr = sub('\w', '', input)
        # separate by comma
        tags = tagstr.split(',')
        # if there are tags left
        if len(tag):
            # for the list of tags left
            for tag in tags:
                # create a new tag for the entry
                entry.create_tag(tag)
    return render_view(
        'tag.html',
        entry=entry,
        slug=slug
        )

# TODONE show entries that have a specific tag
@app.route('/tags/<tagname>')
def show_entries_with_tag(tagname):
    # get distinct tags by tagname
    tags = Tag.select().distinct().where(Tag.tagname == tagname)
    return render_view(
        'entries-by-taglist.html',
        tagname=tagname,
        tags=tags,
    )

# TODONE Selecting tag takes you to a list of specific tags
@app.route('/alltags')
def all_tags():
    # save tags in a list
    alltags = []
    tags = Tag.select(
        Tag.tagname).distinct().order_by(
            Tag.tagname)
    # for each tag
    for tag in tags:
        # if the tag hasn't been noted yet
        if tag.tagname not in alltags:
            # add it to the list of tags
            alltags.append(tag.tagname)
    return render_view(
        'all-tags.html',
        tags=alltags,
    )


# send static files is handled by flask (url_for('static', filename))
if __name__ == '__main__':
    initialize()
    app.run(debug=DEBUG, port=8000)
