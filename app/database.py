import time

from sqlalchemy import create_engine, Column, Integer, String, Float, desc, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UnlockedCars(Base):
    __tablename__ = 'unlocked_cars'

    id = Column(Integer, primary_key=True)
    car_model = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<UnlockedCars(car_model={self.car_model})>"

class Times(Base):
    __tablename__ = 'times'

    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    level = Column(String, nullable=False)
    full_time = Column(Float, nullable=False)
    fastest_lap = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Times(id={self.id})>"

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    last_login = Column(Float)

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
        if session.query(Player).count() == 0:
            session.add(Player(name='Jeff', last_login=time.time()))
            session.commit()
        session.close()

    def add_player(self, name):
        """Add a new player to the database."""
        session = self.Session()

        player = session.query(Player).filter_by(name=name.capitalize())

        # Ensure player doesn't already exist
        if player.count() == 0:
            session.add(Player(name=name.capitalize(), last_login=time.time()))
            session.commit()
            session.close()
            return True
        else:
            player.first().last_login = time.time()
            session.commit()
            session.close()
            return False

    def get_last_player_name(self):
        session = self.Session()
        try:
            player = session.query(Player).order_by(desc(Player.last_login)).first()
            return player.name
        finally:
            session.close()
    def add_time(self, player_name, level, full_time, fastest_lap):
        session = self.Session()

        session.add(Times(player_name=player_name.capitalize(), level=level, full_time=full_time, fastest_lap=fastest_lap))
        session.commit()
        session.close()
        return True

    def get_personal_best(self, player_name, level):
        session = self.Session()
        try:
            best_time = session.query(Times).filter_by(player_name=player_name, level=level).order_by(asc(Times.full_time)).first()
            return best_time.full_time
        except:
            return None
        finally:
            session.close()


    def get_times(self, level):
        session = self.Session()
        times_list = []
        try:
            times = session.query(Times).filter_by(level=level).all()
            for t in times:
                times_list.append((t.player_name, t.full_time, t.fastest_lap))

            return times_list

        except:
            pass
        finally:
            session.close()


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

    def is_car_unlocked(self, car_model):
        session = self.Session()
        try:
            result = session.query(UnlockedCars).filter_by(car_model=car_model).count() > 0
            return result
        finally:
            session.close()

    def unlock_car(self, car_model):
        session = self.Session()
        try:
            if not self.is_car_unlocked(car_model):
                session.add(UnlockedCars(car_model=car_model))
                session.commit()
                return True
            return False
        finally:
            session.close()

    def buy_car(self, car_model, price):
        if self.is_car_unlocked(car_model):
            return True

        coins = self.get_coins()
        if coins >= price:
            session = self.Session()
            try:
                coins_record = session.query(Coins).first()
                coins_record.total_count -= price
                session.commit()
                self.unlock_car(car_model)
                return True
            finally:
                session.close()
        return False