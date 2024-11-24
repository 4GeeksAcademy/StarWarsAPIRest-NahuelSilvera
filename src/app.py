"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users,Planets,Favorites,Characters


app = Flask(__name__)

# La clave super secreta
app.config['SECRET_KEY'] = 'Sesuponequeestodebesersecretisimo' 

jwt = JWTManager(app)


app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#### Endpoints ####

# [POST] /token - Tokenización de usuario

@app.route('/token', methods=['POST'])
def generate_token():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = Users.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "The user o the password are invalid"}), 401

    access_token = create_access_token(
        identity=user.user_id, 
        expires_delta=datetime.timedelta(hours=1)  # El token expira en 1 hora, por seguridad
    )

    return jsonify({'token': access_token}), 200


# [GET] /characters - Obtener todos los personajes
@app.route('/characters', methods=['GET'])
@jwt_required()
def get_all_characters():
    # Accede al usuario autenticado
    current_user_id = get_jwt_identity()

    characters = Characters.query.all()
    characters_list = []
    for character in characters:
        characters_list.append({
            'character_id': character.character_id,
            'name': character.name,
            'species': character.species,
            'homeworld': character.homeworld,
            'gender': character.gender
        })
    
    return jsonify(characters_list), 200

# [GET] /character/<int:character_id> - Obtener la información de un personaje por ID
@app.route('/character/<int:character_id>', methods=['GET'])
@jwt_required()
def get_character(character_id):
    current_user_id = get_jwt_identity()

    character = Characters.query.filter_by(character_id=character_id).first()
    
    if character is None:
        return jsonify({"message": "Character not found"}), 404

    character_data = {
        'character_id': character.character_id,
        'name': character.name,
        'species': character.species,
        'homeworld': character.homeworld,
        'gender': character.gender
    }

    return jsonify(character_data), 200

# [POST] /character - Agregar un personaje
@app.route('/character', methods=['POST'])
@jwt_required()
def add_character():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()

    if 'name' not in data or 'species' not in data or 'homeworld' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_character = Characters(
        name=data['name'],
        species=data['species'],
        homeworld=data['homeworld'],
        gender=data.get('gender', None)
    )

    db.session.add(new_character)
    db.session.commit()

    return jsonify({
        "message": "Character added successfully",
        "character_id": new_character.character_id,
        "name": new_character.name
    }), 201

#  [PUT] /character/<int:character_id> - Modificar personaje
@app.route('/character/<int:character_id>', methods=['PUT'])
@jwt_required()
def update_character(character_id):
    current_user_id = get_jwt_identity()

    data = request.get_json()

    character = Characters.query.get(character_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    character.name = data.get('name', character.name)
    character.species = data.get('species', character.species)
    character.homeworld = data.get('homeworld', character.homeworld)
    character.gender = data.get('gender', character.gender)

    db.session.commit()

    return jsonify({
        "message": "Character updated successfully",
        "character_id": character.character_id,
        "name": character.name
    }), 200

#  [DELETE] /character/<int:character_id> - Eliminar personaje
@app.route('/character/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_character(character_id):
    current_user_id = get_jwt_identity()

    character = Characters.query.get(character_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({
        "message": "Character deleted successfully",
        "character_id": character_id
    }), 200

#### Fin Characters ####

#### Planets ####

# [GET] /planets - Obtener todos los planetas

@app.route('/planets', methods=['GET'])
@jwt_required()
def get_all_planets():
    current_user_id = get_jwt_identity()

    planets = Planets.query.all()
    
    planets_list = []
    for planet in planets:
        planets_list.append({
            'planet_id': planet.planet_id,
            'name': planet.name,
            'climate': planet.climate,
            'terrain': planet.terrain,
            'population': planet.population
        })
    
    return jsonify(planets_list), 200


# [GET] /planet/<int:planet_id> - Obtener la información de un planeta por ID

@app.route('/planet/<int:planet_id>', methods=['GET'])
@jwt_required()
def get_planet(planet_id):
    current_user_id = get_jwt_identity()

    planet = Planets.query.filter_by(planet_id=planet_id).first()
    
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404

    planet_data = {
        'planet_id': planet.planet_id,
        'name': planet.name,
        'climate': planet.climate,
        'terrain': planet.terrain,
        'population': planet.population
    }

    return jsonify(planet_data), 200

# [POST] /planet - Agregar un planeta

@app.route('/planet', methods=['POST'])
@jwt_required()
def add_planet():
    current_user_id = get_jwt_identity()
    
    data = request.get_json()

    if 'name' not in data or 'climate' not in data or 'terrain' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planets(
        name=data['name'],
        climate=data['climate'],
        terrain=data['terrain'],
        population=data.get('population', None)
    )

    db.session.add(new_planet)
    db.session.commit()

    return jsonify({
        "message": "Planet added successfully",
        "planet_id": new_planet.planet_id,
        "name": new_planet.name
    }), 201

#  [PUT] /planet/<int:planet_id> - Modificar planeta de la BD

@app.route('/planet/<int:planet_id>', methods=['PUT'])
@jwt_required()
def update_planet(planet_id):
    current_user_id = get_jwt_identity()

    data = request.get_json()

    planet = Planets.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    planet.name = data.get('name', planet.name)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)
    planet.population = data.get('population', planet.population)

    db.session.commit()

    return jsonify({
        "message": "Planet updated successfully",
        "planet_id": planet.planet_id,
        "name": planet.name
    }), 200


#  [DELETE] /planet/<int:planet_id> - Eliminar planeta de la bd

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_planet(planet_id):
    current_user_id = get_jwt_identity()

    planet = Planets.query.get(planet_id)
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()

    return jsonify({
        "message": "Planet deleted successfully",
        "planet_id": planet_id
    }), 200


#### Fin Planets ####

#### Users ####

# [GET] /users - Listar todos los usuarios

@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()

    users = Users.query.filter_by().all() 

    users_data = [{
        'user_id': user.user_id,
        'email': user.email,
        'username': user.username,
        'user_creation_date': user.user_creation_date
    } for user in users]

    return jsonify(users_data), 200

# [GET] /users/favorites - Listar todos los favoritos del usuario actual

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    current_user_id = get_jwt_identity()

    # Obtener los favoritos del usuario actual.
    favorites = Favorites.query.filter_by(user_id=current_user_id).all()
    favorites_data = []

    for favorite in favorites:
        if favorite.favorite_type == 'Planet':
            planet = Planets.query.get(favorite.item_id)
            if planet:
                favorites_data.append({
                    'favorite_type': favorite.favorite_type,
                    'planet_id': planet.planet_id,
                    'name': planet.name
                })
        elif favorite.favorite_type == 'Character':
            character = Characters.query.get(favorite.item_id)
            if character:
                favorites_data.append({
                    'favorite_type': favorite.favorite_type,
                    'character_id': character.character_id,
                    'name': character.name
                })
    
    return jsonify(favorites_data), 200

# [POST] /favorite/planet/<int:planet_id> - Agregar un nuevo planeta favorito

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
@jwt_required()
def add_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()  # Obtiene el user_id del JWT
    
    # Verificar si el planeta existe.
    planet = Planets.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    # Verificar si ya es favorito
    existing_favorite = Favorites.query.filter_by(
        user_id=current_user_id,
        item_id=planet_id,
        favorite_type="Planet"
    ).first()
    
    if existing_favorite:
        return jsonify({"message": "Planet is already in favorites"}), 400

    # Crear el registro de favorito.
    new_favorite = Favorites(
        user_id=current_user_id,
        item_id=planet_id,
        favorite_type="Planet"
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "message": "Planet added to favorites",
        "planet_id": planet_id,
        "planet_name": planet.name
    }), 201


# [POST] /favorite/character/<int:character_id>' - Agregar un nuevo personaje favorito

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
@jwt_required()
def add_favorite_character(character_id):
    current_user_id = get_jwt_identity()  # Obtiene el user_id del JWT
    
    # Verificar si el personaje existe.
    character = Characters.query.get(character_id)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    # Verificar si ya es favorito
    existing_favorite = Favorites.query.filter_by(
        user_id=current_user_id,
        item_id=character_id,
        favorite_type="Character"
    ).first()
    
    if existing_favorite:
        return jsonify({"message": "Character is already in favorites"}), 400

    # Crear el registro de favorito.
    new_favorite = Favorites(
        user_id=current_user_id,
        item_id=character_id,
        favorite_type="Character"
    )

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({
        "message": "Character added to favorites",
        "character_id": character_id,
        "character_name": character.name
    }), 201

# [DELETE] /favorite/planet/<int:planet_id> - Eliminar un planeta favorito

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_planet(planet_id):
    current_user_id = get_jwt_identity()  # Obtiene el user_id del JWT

    # Buscar el favorito correspondiente.
    favorite = Favorites.query.filter_by(
        user_id=current_user_id,
        item_id=planet_id,
        favorite_type="Planet"
    ).first()

    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite planet removed"}), 200


# [DELETE] /favorite/character/<int:character_id> - Eliminar un character favorito

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
@jwt_required()
def delete_favorite_character(character_id):
    current_user_id = get_jwt_identity()  

    # Buscar el favorito correspondiente.
    favorite = Favorites.query.filter_by(
        user_id=current_user_id,
        item_id=character_id,
        favorite_type="Character"
    ).first()

    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Favorite character removed"}), 200


#### Fin Users  ####



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
