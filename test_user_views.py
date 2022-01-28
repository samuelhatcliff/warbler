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

        msg = Message(
            id=999,
            text="message text",
            user_id=self.testuser.id
        )
        
        db.session.add(msg)
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

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

    def test_add_like_and_show_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id
            
            msg = Message.query.get(999)
            msg_id = msg.id

            resp = c.post(f"/users/add_like/{msg_id}")
            self.assertEqual(resp.status_code, 302)

            user2 = User.query.get(2)
            liked_ids = [l.id for l in user2.likes]

            self.assertIn(msg_id, liked_ids)


            """shows user page"""
            resp = c.get(f"/users/{self.testuser2.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser2", str(resp.data))

            

    def test_add_like_unauth(self):
        """tests that a user can't like their own message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = Message.query.get(999)
            msg_id = msg.id

            resp = c.post(f"/users/add_like/{msg_id}")
            self.assertEqual(resp.status_code, 302)

            user1 = User.query.get(1)
            liked_msgs = user1.likes
            self.assertEqual(len(liked_msgs), 0)


    # def test_remove_like(self):
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id
            
    #         user1 = User.query.get(1)
    #         msg = Message.query.get(999)
           
    #         # user1.likes.append(msg)
    #         resp = c.post(f"/users/add_like/{msg.id}")
    #         # db.session.commit()
    #         resp = c.post(f"/users/add_like/{msg.id}")
    #         self.assertEqual(resp.status_code, 302)
    
    #         liked_ids = [l.id for l in user1.likes]
    #         self.assertNotIn(msg.id, liked_ids)





            











