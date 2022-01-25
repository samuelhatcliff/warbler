"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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

class UserModelTestCase(TestCase):
#     """Test views for messages."""

    def setUp(self):
    #     """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u1.id = 1
        u2 = User.signup("test2", "email2@email.com", "password", None)
        u2.id = 2

        

        user1 = User.query.get(1)
        user2 = User.query.get(2)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
                        

        self.client = app.test_client()
    
    # def tearDown(self):
    #     res = super().tearDown()
    #     db.session.rollback()
    #     return res

    # def test_user_model(self):
    # #     """Does basic model work?"""
    #     user1 = User.query.get(1)


    #     # User should have no messages & no followers
    #     self.assertEqual(len(user1.messages), 0)
    #     self.assertEqual(len(user1.followers), 0)

    # def test_repr_method(self):
        # User.query.delete()
        # u = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        # db.session.add(u)
        # db.session.commit()


        # repr = f"<User #1: testuser, test@test.com>"

        # self.assertEqual(repr, self.u1)

    # def is_following(self):
    #     User.query.delete()
    #     u1 = User(
    #         email="test@test.com",
    #         username="testuser",
    #         password="HASHED_PASSWORD"
    #     )
    #     u2 = User(
    #         email="test@test2.com",
    #         username="testuser2",
    #         password="HASHED_PASSWORD2"
    #     )
    #     u1.following.append(u2)
    #     self.assertIn(u1.following, u2)