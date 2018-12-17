# --------------------------------
# Python Web Development Techdegree
# Project 5 - Flask Journal
# by Maxwell Hunter
# follow me on GitHub @mHunterAK
# --------------------------------

from peewee import (Model, SqliteDatabase,
                    DateTimeField, TextField, IntegerField
                    )  # pragma: no cover
import os

# i
DEBUG = os.environ['FLASK_DEBUG'] is not 'production'

if DEBUG:
    DATABASE = SqliteDatabase('TESTING_flask_journal.db')
else:  # pragma: no cover
    DATABASE = SqliteDatabase('flask_journal.db')

##########
# MODELS #
##########


# create a base model, since every entry uses the same database
class BaseModel(Model):
    # database info
    class Meta:
        database = DATABASE


# create a Peewee model class for journal entries.
class Entry(BaseModel):
    # Title
    title = TextField()
    # Date
    date = DateTimeField()
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
    def create(
        self,
        # Title
        title,
        # Date
        date,
        # Time Spent
        time_spent,
        # What You Learned
        learned="",
        # Resources to Remember
        resources="",
            ):
        return Entry.create(
            # Title
            title=title,
            # Date
            date=date,
            # Time Spent
            time_spent=time_spent,
            # What You Learned
            learned=learned,
            # Resources to Remember
            resources=resources,
        )

    # Add the ability to edit a journal entry
    def edit(
            self,
            # Title
            title,
            # Date
            date,
            # Time Spent
            time_spent,
            # What You Learned
            learned="",
            # Resources to Remember
            resources="",
    ):
        # title
        self.title = title,
        # Date
        self.date = date,
        # Time Spent
        self.time_spent = time_spent,
        # What You Learned
        self.learned = learned,
        # Resources to Remember
        self.resources = resources,

    # Add the ability to delete a journal entry
    def delete(self):
        # goodbye, cruel world
        self.delete_instance()


def initialize():
    # open database connection
    DATABASE.connect()
    # create tables, if they don't exist
    DATABASE.create_tables([Entry], safe=True)
    # close database connection
    DATABASE.close()
    # return success
    return True
