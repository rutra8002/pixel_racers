from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    coin_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Player(name='{self.name}', coins={self.coin_count})>"


class DatabaseManager:
    def __init__(self, db_path='game_data.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.initialize_db()

    def initialize_db(self):
        Base.metadata.create_all(self.engine)

    def add_coin(self, player_name):
        """Increment coin count for the specified player."""
        session = self.Session()

        # Find or create player
        player = session.query(Player).filter_by(name=player_name).first()
        if not player:
            player = Player(name=player_name, coin_count=1)
            session.add(player)
        else:
            player.coin_count += 1

        session.commit()
        session.close()

    def get_player_coins(self, player_name):
        session = self.Session()
        try:
            player = session.query(Player).filter_by(name=player_name).first()

            if not player:
                # Create player
                player = Player(name=player_name, coin_count=0)
                session.add(player)
                session.commit()

            # Get the coin count while session is still open
            return player.coin_count
        finally:
            # Always close the session
            session.close()