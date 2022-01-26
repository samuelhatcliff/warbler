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

        self.u3 = User.signup("test", "test@email.com", "password", None)
        self.u3.id = 3

        self.class_user= u1


        user1 = User.query.get(1)
        user2 = User.query.get(2)

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
                        

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""
        user1 = User.query.get(1)


        # User should have no messages & no followers
        self.assertEqual(len(user1.messages), 0)
        self.assertEqual(len(user1.followers), 0)

    def test_repr_method(self):
        u1 = User.query.get(1)
        user1 = str(u1)

        db.session.add(u1)
        db.session.commit()


        repr = f"<User #1: test1, email1@email.com>"

        self.assertEqual(repr, user1)

    def test_is_following(self):
        u1 = User.query.get(1)
        u2 = User.query.get(2)

        u1.following.append(u2)
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
    #     
    def test_is_followed_by(self):
        u1 = User.query.get(1)
        u2 = User.query.get(2)

        u1.following.append(u2)
        
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def test_user_create(self):
        u1 = User.signup("test1", "email1@email.com", "password", None)
        user1 = str(u1)
        repr = f"<User #{u1.id}: test1, email1@email.com>"
        self.assertEqual(repr, user1)
        self.assertEqual(u1.username, "test1")
        self.assertEqual(u1.email, "email1@email.com")
        self.assertNotEqual(u1.password, "password")

        # self.assertNotIsInstance(u2, User)

    def test_user_create_invalid(self):
        u1 = User.signup(None, "email@gmail.com", "password", None) 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_create_invalid_email(self):
        u2 = User.signup('test1', None, "password", None) 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_create_notunique_email(self):
        u2 = User.signup('test1','test@email.com', "password", None) 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_user_create_notunique_username(self):
        u2 = User.signup('test','test4@email.com', "password", None) 
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_auth(self):
        u1 = User.query.get(1)
        authed = User.authenticate("test1", "password")
        self.assertTrue(authed)
        self.assertIsNotNone(authed)
        self.assertEqual(u1.username, authed.username)
        self.assertEqual(u1.id, authed.id)

    def test_user_auth(self):
        authed = User.authenticate("fadhfaidad", "password")
        self.assertFalse(authed)
        authed2 = User.authenticate("test1", "safdkjsadk")
        self.assertFalse(authed2)
     
