from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# создание соединения с базой данных
engine = create_engine('sqlite:///elements.db')
Session = sessionmaker(bind=engine)

# создание базового класса моделей
Base = declarative_base()


# определение модели элемента
class Element(Base):
    __tablename__ = 'elements'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(String)
    phone = Column(String)
    e_mail = Column(String)
    parent = Column(String)
    parent_phone = Column(String)
    parent_e_mail = Column(String)
    achivements = Column(String)

    def __repr__(self):
        return f'Element(id={self.id}, name={self.name}, age={self.age}, phone={self.phone}, e_mail={self.e_mail}, \
        parent={self.parent}, parent_phone={self.parent_phone}, parent_e_mail={self.parent_e_mail}, \
        achivements={self.achivements})'


# создание таблицы элементов
Base.metadata.create_all(engine)
