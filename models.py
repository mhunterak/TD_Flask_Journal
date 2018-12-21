'''
Python Web Development Techdegree
Project 5 - Flask Journal
by Maxwell Hunter
follow me on GitHub @mHunterAK

    I am aiming for the
    Exceeds Expectations grade on this project!

    models.py is the lowest level script,
    and is only ever imported from higher level script flask_journal.py (views)

'''
# Core
from datetime import datetime as dt  # pragma: no cover
from re import compile, sub  # pragma: no cover
from unicodedata import normalize  # pragma: no cover

# 3rd party
from flask import Markup  # pragma: no cover
from flask_bcrypt import (
    generate_password_hash, check_password_hash)  # pragma: no cover
from flask_login import UserMixin, login_user, logout_user  # pragma: no cover
from peewee import (Model, SqliteDatabase,
                    DateTimeField, TextField, IntegerField, ForeignKeyField,
                    InterfaceError,
                    )  # pragma: no cover

# Global variables
_punct_ = compile(
    r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')  # pragma: no cover
# imported by flask_journal
DEBUG = True

# DB setup
if DEBUG:
    DATABASE = SqliteDatabase('TESTING_flask_journal.db')
else:  # pragma: no cover
    DATABASE = SqliteDatabase('flask_journal.db')

'''
MODELS
'''


# create a base model, since every entry uses the same database
class BaseModel(Model):
    # database info
    class Meta:
        database = DATABASE


# create a Peewee model class for Users
class User(UserMixin, BaseModel):
    # username must be unique
    username = TextField(
        unique=True)
    # both are case-sensitive
    password = TextField(
        )

    @classmethod
    def create_user(self, username, password):
        return self.create(
            username=username,
            # save the user's password as a hash, so no one can hack the
            # database and get the user's passwords
            password=generate_password_hash(password),
        )

    @classmethod
    # main class method for logging in a user
    # checks for a user, and verifies their password
    def login_user(self, username, password):
        user = User.get(User.username == username)
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return True
        return False

    @classmethod
    def logout(self):
        return logout_user()


# create a Peewee model class for journal entries.
class Entry(BaseModel):
    # Title
    title = TextField(
        unique=True,
        null=False,
    )
    # Date
    date = DateTimeField(
        null=False
    )
    # Time Spent
    time_spent = IntegerField()
    # What You Learned
    learned = TextField(
        # can be blank
        null=True,
    )
    # Resources to Remember
    resources = TextField(
        # can be blank
        null=True,
    )

    # override the ability to add a journal entry
    @classmethod
    def create_entry(
        self,
        title,  # Title
        date,  # Date
        time_spent,  # Time Spent
        learned,  # What You Learned
        resources,  # Resources to Remember
            ):
        try:
            return Entry.create(
                # Title
                title=title,
                # Date
                date=dt.strptime(
                    date,
                    '%Y-%m-%d',
                    ),
                # Time Spent
                time_spent=int(time_spent),
                # What You Learned
                learned=str(learned),
                # Resources to Remember
                resources=Markup(resources)
            )
        except InterfaceError:
            print("peewee had an InterfaceError.")

    # Add the ability to edit a journal entry

    def edit(
            self,
            # Title
            title,
            # Date
            date,
            # Time Spent
            time_spent=0,
            # What You Learned
            learned="",
            # Resources to Remember
            resources="",
    ):
        # only update fields that were changed
        # title
        if title:
            self.title = title
        # date
        if date:
            self.date = dt.strptime(
                date,
                '%Y-%m-%d',
                )
        # time spent
        if time_spent:
            self.time_spent = time_spent
        # What You Learned
        if learned:
            self.learned = learned
        # Resources to Remember
        if resources:
            self.resources = resources
        # save back into the database
        self.save()
        # return success if no errors occur
        return True

    # returns the title in slugified form
    def slugify_title(self):
        return self.slugify(
            str(self.title)
            )

    # turns ugly URL`s into nice slug
    # based on code by Amin Ronacher - Generating Slugs (2010-05-03)
    # retreieved from http://flask.pocoo.org/snippets/5/
    @staticmethod
    def slugify(text):
        """Generates an ASCII-only slug."""
        result = []
        for word in _punct_.split(text.lower()):
            word = normalize('NFKC', word)
            if word:
                result.append(word)
        return str(
            '-'.join(result)
        )

    @staticmethod
    # retrieves an entry based on its slug
    def get_entry_from_slug(slug):
        entries = Entry.select()
        for entry in entries:
            if entry.slugify_title() == slug:
                return entry

    # get the datetime string (2016-01-31 format)
    def get_datetime_string(self):
        # get date from datefield
        return self.date.strftime('%Y-%m-%d')

    # from the entry model, return the date as a formatted string
    def get_date_string(self):
        # get date from database
        # saved as a string, convert it do datetime
        try:
            date_as_datetime = dt.strptime(self.date, "%Y-%m-%d")
        # if it's already a datetime (it should be)
        except TypeError:
            date_as_datetime = self.date
        return date_as_datetime.strftime(
                # display formated date
                "%B %d, %Y"
                )

    # converts minutes into larger time increments when appropriate
    def display_time_spent(self):
        # minutes
        if self.time_spent < 60:
            return '{} minutes'.format(self.time_spent)
        # hours
        if self.time_spent < 1440:
            return '{} hours'.format(self.time_spent / 60)
        # days
        if self.time_spent < 10080:
            return '{} days'.format(self.time_spent / 1440)
        # weeks
        if self.time_spent < 44640:
            return '{} weeks'.format(self.time_spent / 10080)
        # years
        else:
            # numbers thanks to:
            # https://www.quora.com/How-many-minutes-are-there-in-a-year
            return '{} years'.format(self.time_spent / 525949)

    # Add the ability to delete a journal entry
    def delete_entry(self):
        # goodbye, cruel world
        with DATABASE.atomic():
            tags = Tag.select().where(Tag.tagged_post == self)
            for tag in tags:
                tag.delete_instance()
            self.delete_instance()

    def add_tags(self, inputstr):
        # separate by comma
        tags = inputstr.split(',')
        for i, tagstr in enumerate(tags):
            # remove whitespace
            tags[i] = sub('\W', '', tagstr)
        # if there are tags left
        if len(tags):
            # for the list of tags left
            for tag in tags:
                if len(tag):
                    # create a new tag for the entry
                    self.create_tag(tag)
            return tags
        else:
            return False

    def create_tag(
        self,
        tagname,
    ):

        existing_tags = Tag.select().where(
            (Tag.tagged_post == self.id)
        )
        for tag in existing_tags:
            if tag.tagname == tagname:
                return tag
        return Tag.create_tag(
            tagname=tagname,
            tagged_post=self,
        )

    def get_tags(self):
        return Tag.select().where(Tag.tagged_post == self).order_by(
            Tag.tagname.asc())


# TODONE XC: Add tags to journal entries in the model.
class Tag(BaseModel):
    tagname = TextField(
        null=False
    )
    tagged_post = ForeignKeyField(
        Entry,
        related_name='tag',
    )

    def create_tag(
        tagname,
        tagged_post
    ):
        return Tag.create(
            tagname=tagname,
            tagged_post=tagged_post,
        )


def initialize():
    # open database connection
    DATABASE.connect()
    # create tables, if they don't exist
    DATABASE.create_tables([Entry, User, Tag], safe=True)
    # close database connection
    DATABASE.close()

    setup_dummy_content()
    # return success
    return True


def setup_dummy_content():
    # if dummy data is not available (No Entries Available)
    try:
        Entry.get()
    except Entry.DoesNotExist:
        print('No Entries Available!')
        print('Initializing default entries')
        default_entries = [
            [
                "The best day I've ever had",
                '2016-01-31',
                900,
                '''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Nunc ut rhoncus felis, vel tincidunt neque. \nCras egestas ac ipsum in posuere.
Fusce suscipit, libero id malesuada placerat, orci velit semper metus, quis
pulvinar sem nunc vel augue. In ornare tempor metus, sit amet congue justo
porta et. Etiam pretium, sapien non fermentum consequat, dolor augue gravida
lacus, non accumsan. Vestibulum ut metus eleifend, malesuada nisl at,
scelerisque sapien.''',
                '''<li><a href="">Lorem ipsum dolor sit amet</a></li>
<li><a href="">Cras accumsan cursus ante, non dapibus tempor</a></li>
<li>Nunc ut rhoncus felis, vel tincidunt neque</li>
<li><a href="">Ipsum dolor sit amet</a></li>
''',
                '',
            ],
            [
                "The absolute worst day I've ever had",
                '2016-01-31',
                900,
                '''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Nunc ut rhoncus felis, vel tincidunt neque. \nCras egestas ac ipsum in posuere.
Fusce suscipit, libero id malesuada placerat, orci velit semper metus, quis
pulvinar sem nunc vel augue. In ornare tempor metus, sit amet congue justo
porta et. Etiam pretium, sapien non fermentum consequat, dolor augue gravida
lacus, non accumsan. Vestibulum ut metus eleifend, malesuada nisl at,
scelerisque sapien.''',
                '',
            ],
            [
                'That time at the mall',
                '2016-01-31',
                900,
                '''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Nunc ut rhoncus felis, vel tincidunt neque. \nCras egestas ac ipsum in posuere.
Fusce suscipit, libero id malesuada placerat, orci velit semper metus, quis
pulvinar sem nunc vel augue. In ornare tempor metus, sit amet congue justo
porta et. Etiam pretium, sapien non fermentum consequat, dolor augue gravida
lacus, non accumsan. Vestibulum ut metus eleifend, malesuada nisl at,
scelerisque sapien.''',
                '',
            ],
            [
                "Dude, where's my car?",
                '2016-01-31',
                900,
                '''Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Nunc ut rhoncus felis, vel tincidunt neque. \nCras egestas ac ipsum in posuere.
Fusce suscipit, libero id malesuada placerat, orci velit semper metus, quis
pulvinar sem nunc vel augue. In ornare tempor metus, sit amet congue justo
porta et. Etiam pretium, sapien non fermentum consequat, dolor augue gravida
lacus, non accumsan. Vestibulum ut metus eleifend, malesuada nisl at,
scelerisque sapien.''',
                '',
            ],
        ]

        # Add default entries
        for entry in default_entries:
            Entry.create_entry(
                title=entry[0],
                date=entry[1],
                time_spent=entry[2],
                learned=entry[3],
                resources=Markup(entry[4])
                ),

        # Add default tags
        entry = Entry.get_entry_from_slug(
            'the-best-day-i-ve-ever-had')
        entry.add_tags('best, day')
        entry = Entry.get_entry_from_slug(
            'the-absolute-worst-day-i-ve-ever-had')
        entry.add_tags('worst, day')

        # Add default user
        User.create_user(
            username="Mhunterak",
            password="password",
        )
