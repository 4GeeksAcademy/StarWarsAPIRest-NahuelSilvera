from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    user_creation_date = db.Column(db.TIMESTAMP, nullable=False)
    favorites = db.relationship("Favorites", back_populates="user")

    def __repr__(self):
        return '<users %r>' % self.username

    def serialize(self):
        return {
            "id": self.user_id,
            "email": self.email,
            "username": self.username
            # do not serialize the password, it's a security breach
        }

class Planets(db.Model):
    __tablename__ = 'planets'
    planet_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    climate = db.Column(db.String(100), nullable=True)
    terrain = db.Column(db.String(100), nullable=True)
    population = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.planet_id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population
        }

class Characters(db.Model):
    __tablename__ = 'characters'
    character_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    species = db.Column(db.String(100), nullable=True)
    homeworld = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<Character %r>' % self.name

    def serialize(self):
        return {
            "id": self.character_id,
            "name": self.name,
            "species": self.species,
            "homeworld": self.homeworld,
            "gender": self.gender
        }

class Favorites(db.Model):
    __tablename__ = 'favorites'
    favorite_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.planet_id'), nullable=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.character_id'), nullable=True)
    favorite_type = db.Column(db.String(50), nullable=False)

    user = db.relationship("Users", back_populates="favorites")
    planet = db.relationship("Planets", backref="favorites")
    character = db.relationship("Characters", backref="favorites")

    def __repr__(self):
        return '<Favorite %r>' % self.favorite_id

    def serialize(self):
        return {
            "id": self.favorite_id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "character_id": self.character_id,
            "favorite_type": self.favorite_type
        }

