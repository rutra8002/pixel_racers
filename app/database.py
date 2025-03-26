from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    # Removed coin_count column

    def __repr__(self):
        return f"<Player(name='{self.name}')>"


class Coins(Base):
    __tablename__ = 'coins'

    id = Column(Integer, primary_key=True)
    total_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Coins(total_count={self.total_count})>"


class DatabaseManager:
    def __init__(self, db_path='game_data.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.initialize_db()

    def initialize_db(self):
        Base.metadata.create_all(self.engine)
        # Ensure there's exactly one entry in the coins table
        session = self.Session()
        if session.query(Coins).count() == 0:
            session.add(Coins(total_count=0))
            session.commit()
        session.close()

    def add_player(self, name):
        """Add a new player to the database."""
        session = self.Session()

        # Ensure player doesn't already exist
        if session.query(Player).filter_by(name=name).count() == 0:
            session.add(Player(name=name))
            session.commit()
            session.close()
            return True
        else:
            session.close()
            return False

    def add_coin(self):
        """Increment the global coin count and ensure player exists."""
        session = self.Session()

        # Increment global coin count
        coins = session.query(Coins).first()
        coins.total_count += 1

        session.commit()
        session.close()

    def get_coins(self):
        """Get the global coin count and ensure player exists."""
        session = self.Session()
        try:
            # Get global coin count
            coins = session.query(Coins).first()
            return coins.total_count
        finally:
            session.close()