from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine('sqlite:///sane_yt_subfeed/resources/permanents.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
PermanentBase = declarative_base()
PermanentBase.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import sane_yt_subfeed.database.models
    import sane_yt_subfeed.database.video
    PermanentBase.metadata.create_all(bind=engine)


