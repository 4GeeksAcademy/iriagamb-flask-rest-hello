import os
from flask import Blueprint, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, CharacterFavorite
from models import db, Character
from models import db, PlanetFavorite
from models import db, Planet
from models import db, User, Gender, PlanetFavorite, Planet


#Usuarios
user_bp = Blueprint('user_routes', __name__)
@user_bp.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        if not users:
            return jsonify({"error": "No users found"}), 400
        serialized_users = [user.serialize() for user in users]
        return jsonify({"users": serialized_users}), 200
    except Exception as error:
        return jsonify({"error":str(error)}), 400

@user_bp.route('/user', methods=['POST'])
def create_user():
    body = request.json

    name = body.get("name", None)
    last_name = body.get("last_name", None)
    gender = body.get("gender", None)
    email = body.get("email", None)
    suscription_date = body.get("suscription_date", None)

    required_fields = ["name", "last_name", "gender", "email", "suscription_date"]

    for field in required_fields:
        if field not in body:
            return jsonify({"error": f"Missing field '{field}'"}),400

    user = User(name=name, last_name=last_name, gender=Gender(gender), email=email, suscription_date=suscription_date)

    try:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        return jsonify({"message": f"User {user.name} created successfully!"}),201
    
    except Exception as error:
        return jsonify({"error": f"{error}"}), 500
    

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "user not found!"}), 404
        return jsonify({"user": user.serialize()}), 200
    except Exception as error:
        return jsonify({"error", f"Missing field {error}"})

user_fav_bp = Blueprint('favorite_user_routes', __name__)

@user_fav_bp.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    try:
        planet_favorites_user = PlanetFavorite.query.filter_by(user_id=user_id).all()
        planet_details = [Planet.query.get(fav.planet_id).serialize() for fav in planet_favorites_user]
        character_favorites_user = CharacterFavorite.query.filter_by(user_id=user_id).all()
        character_details = [Character.query.get(fav.character_id).serialize() for fav in character_favorites_user]

        response = {
            "planets_favorites":planet_details,
            "character_details":character_details
        }
        return jsonify(response), 200
    
    except Exception as error:
        return jsonify({"error": f"{error}" }), 500

#Personajes favoritos

character_fav_bp = Blueprint('character_favorites_routes', __name__)

@character_fav_bp.route('/character_favorites', methods=['GET'])
def get_all_character_favorites():
    try:
        character_favorites = CharacterFavorite.query.all()
        if not character_favorites:
            return jsonify({"error": "No character_favorites found"}), 400
        serialized_character_favorites = [character_favorites.serialize() for character_favorites in character_favorites]
        return jsonify({"character_favorite": serialized_character_favorites}),200

    except Exception as error:
        return jsonify({"error": str({error})}), 400
    
@character_fav_bp.route('/character_favorite/<user_id>/<character_id>', methods=['POST'])
def create_character_favorite_to_user(user_id,character_id):
    body = request.json

    user_id = body.get("user_id",None)
    character_id = body.get("character_id", None)

    if user_id is None or character_id is None:
        return jsonify({"error": "Missing values"}),400
    
    character_favorite_user_exist = CharacterFavorite.query.filter_by(user_id=user_id, character_id=character_id).first()
    if character_favorite_user_exist is not None:
        return jsonify({"error": f"character {character_id} and user {user_id} already exist"}), 400
    
    character_favorites = CharacterFavorite(user_id=user_id, character_id=character_id)

    try:
        db.session.add(character_favorites)
        db.session.commit()
        db.session.refresh(character_favorites)

        return jsonify({"message": f"character_favorite {character_id} with user {user_id} created successfully!"}),201

    except Exception as error:
        return jsonify({"error": f"{error}"}),500

@character_fav_bp.route('/character_favorite/<character_id>', methods=['DELETE'])
def character_fav_deleted(character_id):
    try:
        character_favorites = CharacterFavorite.query.filter_by(character_id=character_id).all()
        if character_favorites is None:
            return jsonify({"error":"character_fav not found"}),404
        
        for fav in character_favorites:
            db.session.delete(fav)
        db.session.commit()

        return jsonify({"message": f"character_fav with id {character_id} is deleted"}),200

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}),500
    
    #Personajes

character_bp = Blueprint('character_routes', __name__)
@character_bp.route('/characters', methods=['GET'])
def get_all_characters():
    try:
        characters = Character.query.all()
        if not characters:
            return jsonify({"error":"No characters found"}), 400
        serialized_characters = [character.serialize() for character in characters]
        return jsonify({"characters": serialized_characters }), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 400


@character_bp.route('/character', methods=['POST'])
def create_character():
    body = request.json

    name = body.get("name", None)
    gender = body.get("gender", None)
    hair_color = body.get("hair_color", None)
    eyes_color = body.get("eyes_color", None)

    required_fields = ["name", "gender", "hair_color", "eyes_color"]

    for field in required_fields:
        if field not in body:
            return jsonify({"error": f"Missing field '{field}'"}),400

    character = Character(name=name, gender=gender, hair_color=hair_color, eyes_color=eyes_color)

    try:
        db.session.add(character)
        db.session.commit()
        db.session.refresh(character)

        return jsonify({"message": f"Character {character.name} created successfully"}), 201

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500
    
    
@character_bp.route('/character/<int:id>', methods=['GET'])
def get_character(id):

    character = Character.query.get(id)
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    
    return jsonify({
        "message": f"Character: {character} founded successfully"
    })

@character_bp.route('/character/<int:id>', methods=['PUT'])
def update_character(id):
    body = request.json

    character = Character.query.get(id)
    if character is None:
        return jsonify({"error": "Character not found"}),404
    
    required_fields = ["name", "gender", "hair_color", "eyes_color"]

    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        return jsonify({"error":f"Missing fields:{', '.join(missing_fields)}"}),400
    
    name = body.get("name",None)
    gender = body.get("gender",None)
    hair_color = body.get("hair_color",None)
    eyes_color = body.get("eyes_color",None)

    character.name = name
    character.gender = gender
    character.hair_color = hair_color
    character.eyes_color = eyes_color

    try:
        db.session.commit()
        return jsonify({"character":character.serialize()})
    
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}),500



@character_bp.route('/character/<int:id>', methods=['DELETE'])
def deleted_character(id):
    try:
        character = Character.query.get(id)
        if character is None:
            return jsonify({"error":"character not found"}),404
        db.session.delete(character)
        db.session.commit()

        return jsonify({"message":f"character with id {id} deleted"}),200    

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}),500
    
#Planetas favoritos

planet_fav_bp = Blueprint('planet_favorites_routes', __name__)

@planet_fav_bp.route('/planet_favorites', methods=['GET'])
def get_all_planet_favorites():
    try:
        planet_favorites = PlanetFavorite.query.all()
        if not planet_favorites:
            return jsonify({"error":"No planet_favorites found"}), 400
        serialized_planet_favorites = [planet_favorite.serialize() for planet_favorite in planet_favorites]
        return jsonify({"planet_favorite":serialized_planet_favorites}), 200
    except Exception as error:
        return jsonify({"error", str(error)}),400
    
@planet_fav_bp.route('/planet_favorite/<int:user_id>/<int:planet_id>', methods=['POST'])
def create_favorite_planet_to_user(user_id, planet_id):

    body = request.json

    user_id = body.get("user_id", None)
    planet_id = body.get("planet_id", None)

    if user_id is None or planet_id is None:
        return jsonify({"error", "Missing values"}), 400
    
    planet_favorite_user_exist = PlanetFavorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if planet_favorite_user_exist is not None:
        return jsonify({"error": f"planet {planet_id} and user {user_id} already exist"}),400

    planet_favorite = PlanetFavorite(user_id=user_id, planet_id=planet_id)

    try:
        db.session.add(planet_favorite)
        db.session.commit()
        db.session.refresh(planet_favorite)

        return jsonify({"message": f"planet_favorite {planet_id} with user {user_id} created successfully!"}), 201
    except Exception as error:
        return jsonify({"error": f"{error}"}),500

@planet_fav_bp.route("/planet_favorite/<int:planet_id>", methods=["DELETE"])
def planet_fav_deleted(planet_id):
    try:
        planet_favorites = PlanetFavorite.query.filter_by(planet_id=planet_id).all()
        if planet_favorites is None:
            return jsonify({"error": "planet_fav not found"}), 404
        
        for fav in planet_favorites:
            db.session.delete(fav)
        db.session.commit()

        return jsonify({"message":f"planet_fav with id {planet_id} deleted"}),200
        
    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}),500

 #Planetas   

planet_bp = Blueprint('planet_routes', __name__)



@planet_bp.route('/planets', methods=['GET'])
def get_all_planets():
    try:
        planets = Planet.query.all()
        if not planets:
            return jsonify({"error":"No planets found"}), 400
        serialized_planets = [planet.serialize() for planet in planets]
        return jsonify({"planets":serialized_planets}), 200
    except Exception as error:
        return jsonify({"error", str(error)}),400


@planet_bp.route('/planet', methods=['POST'])
def create_planet():

    body = request.json

    name = body.get("name", None)
    population = body.get("population", None)
    terrain = body.get("terrain", None)
    surface_water = body.get("surface_water", None)
    gravity = body.get("gravity", None)

    required_fields = ["name", "population", "terrain", "surface_water", "gravity"]

    for field in required_fields:
        if field not in body:
            return jsonify({"error": f"Missiong field {field}"}),400
        
    planet = Planet(name=name, population=population, terrain=terrain, surface_water=surface_water, gravity=gravity)

    try:
        db.session.add(planet)
        db.session.commit()
        db.session.refresh(planet)

        return jsonify({"message": f"Planet {planet.name} created successfully"})

    except Exception as error:
        return jsonify({"error": f"{error}"}), 500

@planet_bp.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    
    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({"error":"Planet not found"}), 404
    
    return jsonify({
        "message": f"Planet:{planet} founded successfully"
    })

@planet_bp.route('/planet/<int:id>', methods=['PUT'])
def update_planet(id):
    body = request.json

    planet = Planet.query.get(id)
    if planet is None:
        return jsonify({"error": "Planet not found"}),404
    
    required_fields = ["name", "population", "terrain", "surface_water", "gravity"]

    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}),400
    
    name = body.get("name")
    population = body.get("population")
    terrain = body.get("terrain")
    surface_water = body.get("surface_water")
    gravity = body.get("gravity")

    planet.name = name
    planet.population = population
    planet.terrain = terrain
    planet.surface_water = surface_water
    planet.gravity = gravity

    try:
        db.session.commit()
        return jsonify({"planet":planet.serialize()}),200

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": str(error)}),500


@planet_bp.route('/planet/<int:id>', methods=['DELETE'])
def deleted_planet(id):
    try:
        planet = Planet.query.get(id)
        if planet is None:
            return jsonify({"error":"planet not found"}),404
        db.session.delete(planet)
        db.session.commit()

        return jsonify({"message":f"planet with id {id} deleted"}),200

    except Exception as error:
        db.session.rollback()
        return jsonify({"error": f"{error}"}),500
    
