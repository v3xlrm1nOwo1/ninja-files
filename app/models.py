from app import app
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///NinjaFiles.db'
db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.jpg')
    bio = db.Column(db.String(5000), default='')
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<username {self.username}>"
    

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cover_image = db.Column(db.String(100), nullable=False, default=name)
    user_id = db.Column(db.Integer)
    bio = db.Column(db.String(5000), nullable=False)
    file_type = db.Column(db.String(20))
    extension = db.Column(db.String(20))
    
    def __repr__(self):
        return f"<ID {self.id}>"
    