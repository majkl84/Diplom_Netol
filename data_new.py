import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///db.sqlite')
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

# добавление записи в бд
def add_user(profile_id, worksheet_id):
    with Session() as session:
        to_db = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_db)
        session.commit()

# извлечение записей из БД
def check_user(profile_id, worksheet_id):
    with Session() as session:
        from_db = session.query(Viewed).filter(
            Viewed.profile_id == profile_id,
            Viewed.worksheet_id == worksheet_id
        ).first()
        return True if from_db else False
def delete_worksheets_in_db(profile_id):
    with Session() as session:
        session.query(Viewed).filter(
            Viewed.profile_id == profile_id
        ).delete()
        session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    # add_user(2113, 124512)
    # res = check_user(2113, 1245121)
    # print(res)