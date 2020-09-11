class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "outdoor_activities"


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "test"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "test"
    SQLALCHEMY_ECHO = False
