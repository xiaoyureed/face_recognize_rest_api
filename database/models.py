from database.exts import db


# consumer
class Consumer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    pwd = db.Column(db.String(50))


class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_key = db.Column(db.String(50))
    secret_key = db.Column(db.String(50))


class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    id_car = db.Column(db.String(50))
    arr = db.Column(db.String(4000))
