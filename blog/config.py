import os

class DevelopmentConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://ericsokolov:thinkful@localhost:5432/blogful"
    DEBUG = True