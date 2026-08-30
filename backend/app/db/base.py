from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models.

    Alembic imports this module so that ``Base.metadata`` sees every model for
    autogeneration. New model modules must be imported in ``app/models/__init__.py``.
    """
