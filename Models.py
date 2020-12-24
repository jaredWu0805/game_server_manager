from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Table of Game servers
class GameServers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_ip = db.Column(db.String(80), unique=True, nullable=False)
    client_ip = db.Column(db.String(80), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    last_connection_at = db.Column(db.DateTime, nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Gserver id:{0} ip:{1}>'.format(self.id, self.ip)


class StreamList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_ip = db.Column(db.String(32), unique=True, nullable=False)
    client_ip = db.Column(db.String(32), unique=True, nullable=False)
    client_username = db.Column(db.String(62), nullable=True)
    game_title = db.Column(db.String(64), nullable=False)
    num_of_audience = db.Column(db.Integer, default=0)
    started_from = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Game: {0}, Server ip: {1}, num of audience: {2}'.format(self.game_title,
                                                                        self.server_ip, self.num_of_audience)


class WaitingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_ip = db.Column(db.String(32), unique=True, nullable=False)
    server_ip = db.Column(db.String(32), unique=True, nullable=False)

# Way to add new table
# StreamList.__table__.create(db.session.bind)
