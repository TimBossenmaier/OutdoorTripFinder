import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '7lY6EcdK9MJA79N3oHKG'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'posteo.de')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = '[OutdoorTrips]'
    MAIL_SENDER = 'OutdoorTrips Service <outdoor-trips@posteo.de>'
    ADMIN = os.environ.get('ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEV_DATABASE_USER = os.environ.get('DEV_DATABASE_USER')
    DEV_DATABASE_PASSWORD = os.environ.get('DEV_DATABASE_PASSWORD')
    DEV_DATABASE_NAME = os.environ.get('DEV_DATABASE_NAME')
    DEV_DATABASE_HOST = os.environ.get('DEV_DATABASE_HOST')
    PROD_DATABASE_USER = os.environ.get('PROD_DATABASE_USER')
    PROD_DATABASE_PASSWORD = os.environ.get('PROD_DATABASE_PASSWORD')
    PROD_DATABASE_NAME = os.environ.get('PROD_DATABASE_NAME')
    PROD_DATABASE_HOST = os.environ.get('PROD_DATABASE_HOST')
    TEST_DATABASE_USER = os.environ.get('TEST_DATABASE_USER')
    TEST_DATABASE_PASSWORD = os.environ.get('TEST_DATABASE_PASSWORD')
    TEST_DATABASE_NAME = os.environ.get('TEST_DATABASE_NAME')
    TEST_DATABASE_HOST = os.environ.get('TEST_DATABASE_HOST')
    PATH_PDF_STORAGE = os.environ.get('PDF_STORAGE')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATBASE_URL') or \
                              'postgresql://{}:{}@{}/{}'.format(Config.DEV_DATABASE_USER, Config.DEV_DATABASE_PASSWORD,
                                                                Config.DEV_DATABASE_HOST, Config.DEV_DATABASE_NAME)


class ProductionConfig(Config):
    SQLALCHEMY_DATABSE_URI = os.environ.get('PROD_DATABASE_URL') or \
                             'postgresql://{}:{}@{}/{}'.format(Config.PROD_DATABASE_USER, Config.PROD_DATABASE_PASSWORD,
                                                               Config.PROD_DATABASE_HOST, Config.PROD_DATABASE_NAME)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or \
                              'postgresql://{}:{}@{}/{}'.format(Config.TEST_DATABASE_USER,
                                                                Config.TEST_DATABASE_PASSWORD,
                                                                Config.TEST_DATABASE_HOST, Config.TEST_DATABASE_NAME)


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
