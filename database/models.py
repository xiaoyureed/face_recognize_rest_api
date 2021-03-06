from database.exts import db


class Consumer(db.Model):
    """api 调用者"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    pwd = db.Column(db.String(50))


class Key(db.Model):
    """api key记录表"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    consumer_id = db.Column(db.Integer)
    api_key = db.Column(db.String(50))
    secret_key = db.Column(db.String(50))
    name = db.Column(db.String(50))


class Face(db.Model):
    """人脸数据表"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    id_card = db.Column(db.String(50))
    arr = db.Column(db.String(4000))
    consumer_id = db.Column(db.Integer)
