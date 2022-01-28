"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser.id=1
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser2.id=2

        user2 = User.query.get(2)
        self.testuser.following.append(user2)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})
        
            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_delete_message(self):
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            

            resp = c.post("/messages/new", data={"text": "Hello"})
        
            
            self.assertEqual(resp.status_code, 302)

            
            msg = Message.query.one()
            id = msg.id
            resp = c.post(f"/messages/{id}/delete", follow_redirects=True )
            messages = Message.query.all()
            self.assertEqual(len(messages), 0)
    

    def test_add_message_loggedout(self):
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello23456789"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = str(resp.data)
            self.assertIn("Access unauthorized", html)

    def test_delete_message_loggedout(self):
         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            

            resp = c.post("/messages/new", data={"text": "Hello"})
        
            
            self.assertEqual(resp.status_code, 302)

            
            msg = Message.query.one()
            id = msg.id
            
            
            sess[CURR_USER_KEY] = None
            resp = c.post(f"/messages/{id}/delete", follow_redirects=True )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(Message.query.all()),0)



    def test_delete_message_wrong_user(self):
        msg = Message(
            id=10,
            text="message text",
            user_id=self.testuser2.id
        )
        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post("/messages/10/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            msg = Message.query.get(10)
            self.assertIsNotNone(msg)

    def test_add_message_wrong_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 12345
            resp = c.post("/messages/new", data={"text": "Hello", "user_id": 3})
            self.assertEqual(resp.status_code, 302)

            resp = c.post("/messages/new", data={"text": "Hello", "user_id": 3}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    
    def test_view_follows(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        

        user2 = User.query.get(2)

        

        resp = c.get("/users/1/following")
        self.assertEqual(resp.status_code, 200)



        html = str(resp.data)
        self.assertIn(str(user2.username), html)

    def test_view_followers(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        user1 = User.query.get(1)
        resp = c.get("/users/2/followers")
        html = str(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(str(user1.username), html)


    def test_redirect_follows(self):

        with self.client as c:
            

            user2 = User.query.get(2)

            resp = c.get("/users/1/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            html = str(resp.data)
            self.assertNotIn(str(user2.username), html)
            self.assertIn("Access unauthorized", html)













