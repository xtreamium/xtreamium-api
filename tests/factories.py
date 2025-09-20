import factory
import uuid
from datetime import datetime, timezone
from factory import Faker
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.server import Server
from app.models.channel import Channel
from app.models.epg import EPG
from app.models.programme import Programme


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    email = Faker("email")
    hashed_password = factory.LazyFunction(
        lambda: "$2b$12$bKbjutBQu8g./K50qXPmku..De7DVllt1yBMuFhbQWIZ/tjms.h7m"  # "secret"
    )
    date_created = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    date_last_updated = factory.LazyFunction(lambda: datetime.now(timezone.utc))


class ServerFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Server
        sqlalchemy_session_persistence = "commit"

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = Faker("company")
    url = Faker("url")
    username = Faker("user_name")
    password = Faker("password")
    epg_url = Faker("url")
    owner = factory.SubFactory(UserFactory)


class ChannelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Channel
        sqlalchemy_session_persistence = "commit"

    xmltv_id = Faker("word")
    display_names = factory.LazyFunction(lambda: '["Test Channel"]')
    icons = factory.LazyFunction(lambda: '[{"src": "http://example.com/icon.png"}]')
    urls = factory.LazyFunction(lambda: '["http://example.com"]')
    user = factory.SubFactory(UserFactory)
    server = factory.SubFactory(ServerFactory)


class EPGFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EPG
        sqlalchemy_session_persistence = "commit"

    programs_data = factory.LazyFunction(lambda: '{"programs": []}')
    program_count = Faker("random_int", min=0, max=100)
    user = factory.SubFactory(UserFactory)
    server = factory.SubFactory(ServerFactory)


class ProgrammeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Programme
        sqlalchemy_session_persistence = "commit"

    start_time = Faker("word")  # Stored as string in the model
    stop_time = Faker("word")
    titles = factory.LazyFunction(lambda: '[{"text": "Test Programme"}]')  # JSON
    descriptions = factory.LazyFunction(lambda: '[{"text": "Test description"}]')  # JSON
    channel = factory.SubFactory(ChannelFactory)


def create_test_user(db_session: Session, **kwargs) -> User:
    """Create a test user with optional overrides."""
    UserFactory._meta.sqlalchemy_session = db_session
    return UserFactory(**kwargs)


def create_test_server(db_session: Session, **kwargs) -> Server:
    """Create a test server with optional overrides."""
    ServerFactory._meta.sqlalchemy_session = db_session
    return ServerFactory(**kwargs)


def create_test_channel(db_session: Session, **kwargs) -> Channel:
    """Create a test channel with optional overrides."""
    ChannelFactory._meta.sqlalchemy_session = db_session
    return ChannelFactory(**kwargs)


def create_test_epg(db_session: Session, **kwargs) -> EPG:
    """Create a test EPG with optional overrides."""
    EPGFactory._meta.sqlalchemy_session = db_session
    return EPGFactory(**kwargs)


def create_test_programme(db_session: Session, **kwargs) -> Programme:
    """Create a test programme with optional overrides."""
    ProgrammeFactory._meta.sqlalchemy_session = db_session
    return ProgrammeFactory(**kwargs)
