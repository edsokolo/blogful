import os
import unittest
import multiprocessing
import time
from urlparse import urlparse
from selenium import webdriver

from werkzeug.security import generate_password_hash
from splinter import Browser

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TravisConfig"

from blog import app
from blog.database import Base, engine, session, User, Entry

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.browser = Browser("chrome")

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(1)

    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "alice@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/")

    def test_login_incorrect(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "bob@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")

    def test_add_entry(self):
        self.test_login_correct()
        self.browser.visit("http://127.0.0.1:8080/entry/add")
        self.browser.fill("title", "test title")
        self.browser.fill("content", "test content")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()

        entry = session.query(Entry).all()[0]

        self.assertEqual(entry.title, "test title")
        self.assertEqual(entry.content, "test content")

    def test_edit_entry(self):
        self.test_add_entry()
        self.browser.visit("http://127.0.0.1:8080/entry/0/edit")
        self.browser.fill("title", "test title + edit")
        self.browser.fill("content", "test content + edit")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()

        entry = session.query(Entry).all()[0]

        self.assertEqual(entry.title, "test title + edit")
        self.assertEqual(entry.content, "test content + edit")

    def test_delete_entry(self):
        self.test_add_entry()
        self.browser.visit("http://127.0.0.1:8080/entry/0/delete")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()

        entries = session.query(Entry).count()

        self.assertEqual(entries, 0)

    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()