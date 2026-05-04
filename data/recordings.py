import sqlalchemy
from sqlalchemy import orm
from db_session import SqlAlchemyBase
from datetime import datetime


class Recording(SqlAlchemyBase):
    __tablename__ = 'recordings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)
    track_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    track_title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    track_artist = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now)

    user = orm.relationship('User', back_populates='recordings')