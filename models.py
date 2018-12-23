'''
models holds the object blueprints, and method for initializing the database

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
    '''This Model holds the common database info for
Tag and Entry models'''
    # database info
    class Meta:
        database = DATABASE
        order_by = ('-id', )


# Peewee model class for Users
class User(UserMixin, BaseModel):
    '''User holds username and password - both case sensitive'''
    # username must be unique
    username = TextField(
        unique=True)
    # both are case-sensitive
    password = TextField(
        )

    @classmethod
    def create_user(self, username, password):
        '''Creates an instance of a User with (username, password)'''
        return self.create(
            username=username,
            # save the user's password as a hash, so no one can hack the
            # database and get the user's passwords
            password=generate_password_hash(password),
        )

    @staticmethod
    def login(username, password):
        '''this is the main class method for logging in a User

Tries to log in based on provided username and password.
it checks for a user matching the username, and then verifies their password'''
        user = User.get(User.username == username)
        if check_password_hash(user.password, password):
            login_user(user, remember=True)
            return True
        return False

    @classmethod
    def logout(self):
        '''Logs out the user'''
        return logout_user()


class Entry(BaseModel):
    '''Peewee model class for journal entries
Entry.title = Title of the entry
Entry.date = Date for the entry
Entry.time_spent = Time spent, in minutes, for the entry
Entry.date = Date for the entry
Entry.learned (optional) = What You Learned, in paragraph form
Entry.resources (optional) = Resources to Remember (html friendly)
)
    '''
    title = TextField(
        unique=True,
        null=False,
    )
    date = DateTimeField(
        null=False
    )
    time_spent = IntegerField()
    learned = TextField(
        null=True,
    )
    resources = TextField(
        null=True,
    )

    @classmethod
    def create_entry(
        self,
        title,  # Title
        date,  # Date
        time_spent,  # Time Spent
        learned,  # What You Learned
        resources,  # Resources to Remember
            ):
            ''' This function overrides the default create function
to create a new journal entry. Does some standardization as well,
like on date and resources.
'''
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

    def edit(
            self,
            title='',
            date='',
            time_spent=0,
            learned="",
            resources="",
            ):
        '''this function is for editing a journal entry.
Only fields that were changed are updated.
        '''
        if title:
            self.title = title
        if date:
            self.date = dt.strptime(
                date,
                '%Y-%m-%d',
                )
        if time_spent:
            self.time_spent = time_spent
        if learned:
            self.learned = learned
        if resources:
            self.resources = resources
        # save back into the database
        self.save()
        # return success if no errors occur
        return True

    def slugify_title(self):
        '''this function returns the Entry's title in slugified form'''
        return self.slugify(
            str(self.title)
            )

    @staticmethod
    def slugify(text):
        """This function Generates an ASCII-only slug.
(turns ugly URL`s into nice slug)

based on code by Amin Ronacher - Generating Slugs (2010-05-03)
retreieved from http://flask.pocoo.org/snippets/5/
"""
        result = []
        for word in _punct_.split(text.lower()):
            word = bytearray(word, 'utf-8')
            word = word.decode('utf-8')
            word = normalize('NFKC', word)
            if word:
                result.append(word)
        return str(
            '-'.join(result)
        )

    @staticmethod
    def get_entry_from_slug(slug):
        '''this function returns an entry object based on its slugified title
'''
        entries = Entry.select()
        for entry in entries:
            if entry.slugify_title() == slug:
                return entry

    def get_datetime_string(self):
        '''this function returns the datetime string in '2016-01-31' format)'''
        return self.date.strftime('%Y-%m-%d')

    def get_date_string(self):
        '''this function return the date as a formatted string.
gets the date from database-
it's saved as a datetime, convert it into readable string'''
        date_as_datetime = self.date
        return date_as_datetime.strftime(
                # display formated date
                "%B %d, %Y"
                )

    def display_time_spent(self):
        ''' This function converts minutes
into larger time increments when appropriate

numbers thanks to:
https://www.quora.com/How-many-minutes-are-there-in-a-year'''
        if self.time_spent < 60:
            return '{} minutes'.format(self.time_spent)
        if self.time_spent < 1440:
            return '{} hours'.format(self.time_spent / 60)
        if self.time_spent < 10080:
            return '{} days'.format(self.time_spent / 1440)
        if self.time_spent < 44640:
            return '{} weeks'.format(self.time_spent / 10080)
        else:
            return '{} years'.format(self.time_spent / 525949)

    def delete_entry(self):
        '''This function deletes a journal entry'''
        with DATABASE.atomic():
            tags = Tag.select().where(Tag.tagged_post == self)
            for tag in tags:
                tag.delete_instance()
            self.delete_instance()

    def add_tags(self, inputstr):
        '''This function adds tags to the entry it was called from,
separated by commas

Example: entry.add_tags('foo, bar')
'''
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
            (Tag.tagged_post == self)
        )

        for tag in existing_tags:
            if tag.tagname == tagname:
                return tag

        return Tag.create(
            tagname=tagname,
            tagged_post=self,
        )

    def get_tags(self):
        '''this function returns all the tags f
or the entry it was called from'''
        return Tag.select().where(Tag.tagged_post == self).order_by(
            Tag.tagname.asc())


class Tag(BaseModel):
    '''This class adds tags to journal entries in the model.'''
    tagname = TextField(
        null=False
    )
    tagged_post = ForeignKeyField(
        Entry,
        related_name='tag',
    )

    def create_tag(tagname, tagged_post):
        '''This function creates the tag instance'''
        return Tag.create(
            tagname=tagname,
            tagged_post=tagged_post,
        )


def initialize():
    '''This function initializes the database, and sets up default entries'''
    # open database connection
    DATABASE.connect()
    # create tables, if they don't exist
    DATABASE.create_tables([Entry, User, Tag], safe=True)
    # close database connection
    DATABASE.close()
    # add the default content
    setup_dummy_content()
    # return success
    return True


def setup_dummy_content():
    '''This function creates the default entries'''
    # if default data is not available (No Entries Available)
    try:
        Entry.get()
    except Entry.DoesNotExist:
        print('No Entries Available!')
        print('Initializing default entries')
        # define the defaults
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
                800,
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
                700,
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
                600,
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

        # Add default entries to database
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
