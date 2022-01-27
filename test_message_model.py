"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc


from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
#     """Test views for messages."""

    def setUp(self):
    #     """Create test client, add sample data."""

        db.drop_all()
        db.create_all()


        self.u1 = User.signup("test", "test@email.com", "password", None)
        self.u1.id = 1



        user1 = User.query.get(1)


        db.session.add(user1)
        db.session.commit()

                        

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_add_message(self):
        msg1 = Message(text="message content", user_id=self.u1.id)

        self.u1.messages.append(msg1)
        db.session.add(msg1)
        db.session.commit()
        
        self.assertEqual(len(self.u1.messages), 1)

    def test_add_message_content(self):
        msg1 = Message(text="message content", user_id=self.u1.id)
        self.u1.messages.append(msg1)
        db.session.add(msg1)
        db.session.commit()
        first_msg = str(User.query.get(self.u1.id).messages[0].text)

        self.assertEqual(first_msg, "message content")

    def test_verify_message_user(self):
        msg1 = Message(text="message content", user_id=self.u1.id, id=5)
        # why doesnt the id auto-generate???
        self.u1.messages.append(msg1)
        msg1_id = int(msg1.id)
        db.session.add(msg1)
        db.session.commit()

        msg1_got = Message.query.get(msg1_id)
        self.assertEqual(msg1_got.user.id, self.u1.id)
        self.assertEqual(msg1_got.user.username, self.u1.username)

    def test_userid_is_user_id(self):
        msg1 = Message(text="message content", user_id=self.u1.id, id=5)
        msg1_id = int(msg1.id)
        db.session.add(msg1)
        db.session.commit()

        msg1_got = Message.query.get(msg1_id)
        self.assertEqual(msg1_got.user.id, msg1.user_id)

    def test_message_likes(self):
        msg1 = Message(text="message content", user_id=self.u1.id, id=5)
        usr1 = self.u1
        usr1.likes.append(msg1)
        self.assertEqual(usr1.likes[0].text, "message content")















