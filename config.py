class Config:
    SQLALCHEMY_DATABASE_URI = \
        "mysql+pymysql://root:root@localhost/lost_found_db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = "lostfoundsecretkey"