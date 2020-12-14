"""
Copyright (c) 2020 OneUpPotato

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from sqlalchemy import Integer, BigInteger, Column, String, create_engine, literal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///data.db', echo=False)
Base = declarative_base()


class WeeklyScores(Base):
    __tablename__ = 'weekly_scores'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    score = Column(Integer)

    def __repr__(self):
        return f"WeeklyScores('{self.username}', {self.score})"


Base.metadata.create_all(engine)

session_maker = sessionmaker(bind=engine)
Session = scoped_session(session_maker)
