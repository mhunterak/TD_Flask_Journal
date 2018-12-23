'''
Python Web Development Techdegree
Project 5 - Flask Journal
by Maxwell Hunter
follow me on GitHub @mHunterAK

flask_journal.py
    Main app script, that houses the flask script and view rendering

I am aiming for the
Exceeds Expectations grade on this project!
'''

# Core
from random import choice as random_choice  # pragma: no cover
# 3rd party
from flask import (   # pragma: no cover
    Flask,
    request, flash,
    Markup, render_template, redirect, url_for
    )
from flask_login import (  # pragma: no cover
    LoginManager, login_required)
# Custom
from models import (
    DEBUG,  # Global variables
    Entry, User, Tag,  # Model objects
    initialize  # functions
)

# app initialization
app = Flask(__name__, static_url_path='/static')
# build secret key with hexadecimal (needed for flash messages)
key_choices = u'abcdef0123456789'
key = ''
for i in range(32):
    key += random_choice(key_choices)
app.secret_key = key

# user management initialization
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    '''This function loads the user with login_manager'''
    try:
        return User.get(User.id == userid)
    except User.DoesNotExist:
        return None


@app.route('/logout')
def logout():
    '''This function logs the user out of the app'''
    User.logout()
    flash("You've been logged out", 'success')
    return redirect(url_for('index'))


# ##### #
# VIEWS #
# ##### #
# this is the main script,
# because routing must occur in the same file as app
def render_view(page, **kwargs):
    '''this function renders the template with default information that every
template uses '''
    return render_template(
        page,
        copyright='2018 Maxwell Hunter',
        last_update='2018-12-20',
        **kwargs
    )


@app.route('/login', methods=('GET', 'POST'))
def login():
    '''XC Requirement: password protection / user login
(implements flask_login)

This function, on form submit, implements User.login() function for user login.
Username and Password variables are taken directly from the form.

credentials are provided for the default user in README.md'''
    # if the user is submitting a form
    if request.method == "POST":
        # see if they're redirected from another page
        # because they weren't logged in
        next = request.args.get('next')
        # try to log them in
        # log them in
        if User.login(
                request.form['username'],
                request.form['password']):
            # show login message
            flash('Log in successful, welcome back {}'.format(
                request.form['username']))
            if next:
                # if there's another page to forward to after logging in
                # forward them to that page
                return redirect(next)
            else:
                # if there's nowhere to forward to, send them to the index page
                return redirect(url_for('index'))
        else:
            # if the username or password is invalid, tell them so
            flash("Username or password invalid, please try again")
    # if they're not submitting a form, render the login form
    return render_view('login.html')


@app.route('/index.html')
@app.route('/')
def index():
    ''' necessary routes for the application
the index page looked like a list of entries to me,
so I moved index.html to /entries and had it forward'''
    return redirect(
        url_for('entry_list')
        )


@app.route('/entries')
@app.route('/entries/')
def entry_list():
    ''' Route for entries list
Title is hyperlinked to the detail page for each journal entry

The list view contains a list of journal entries, which displays Title and
Date for Entry.

'''
    # The list view contains:
    entries = Entry.select()
    # a list of journal entries,
    return render_view(
        # which displays
        # Title and Date for Entry
        'index.html',
        entries=entries)


@app.route('/entry')
@app.route('/entries/add', methods=('GET', 'POST'))
@app.route('/entries/add/', methods=('GET', 'POST'))
@login_required
def add():
    '''This function adds an entry'''
    # if the form is submitted
    if request.method == 'POST':
        # connected 'create_entry' class methed from Entry
        try:
            entry = Entry.create_entry(
                title=request.form['title'],
                date=request.form['date'],
                time_spent=request.form['timeSpent'],
                learned=request.form['whatILearned'],
                resources=request.form['ResourcesToRemember'],
            )
            # tell them the entry was created
            flash('Entry #{} created'.format(entry.id))
            return redirect(url_for(
                'details_by_slug',
                slug=entry.slugify_title()))
        except ValueError:
            flash('Invalid Submission')
    # forward to the details page
    return render_view('new.html')


# ### Entry Details


@app.route('/entries/<slug>')
@app.route('/entries/<slug>/details')
def details_by_slug(slug):
    '''This function creates the 'details' view with the route '/details'
displaying the journal entry with all fields:
    '''
    entry = Entry.get_entry_from_slug(slug)
    if entry is None:
        flash("no entry found")
    return render_view(
        'detail.html',
        Markup=Markup,
        entry=entry,
        slug=slug,
        )


@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit_entry(slug):
    '''This function renders the edit entry page,
and handles the POST for form submission'''
    # get the entry from slug
    entry = Entry.get_entry_from_slug(slug)
    # if the form is submitted
    if request.method == 'POST':
        # if the edit is successful
        if entry.edit(
            title=request.form['title'],
            date=request.form['date'],
            time_spent=request.form['timeSpent'],
            learned=request.form['whatILearned'],
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


@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
@login_required
def delete_entry(slug):
    '''This function deletes the entry on submit confirmation
requires 'POST' nethod to actually delete
    '''
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
    '''This route is for adding new tags to an entry'''
    # get entry
    entry = Entry.get_entry_from_slug(slug)
    # if the form is submitted,
    if request.method == 'POST':
        entry.add_tags(request.form['tags'])
    # if not submitting, render the form
    return render_view(
        'tag.html',
        entry=entry,
        slug=slug
        )


@app.route('/tags/<tagname>')
def show_entries_with_tag(tagname):
    '''This route shows entries that have a specific tag'''
    # get distinct tags by tagname
    tags = Tag.select().distinct().where(Tag.tagname == tagname)
    return render_view(
        'entries-by-taglist.html',
        tagname=tagname,
        tags=tags,
    )


@app.route('/alltags')
def all_tags():
    ''' This route shows all tags in use.
    Selecting a tag takes you to a list of specific tags'''
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
