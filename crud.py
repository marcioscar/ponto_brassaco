from datetime import datetime
from pymongo import MongoClient
import pymongo
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

from datetime import datetime, timezone, timedelta, time



try:
    # start example code here
    load_dotenv()
    uri = os.getenv("DATABASE_URL")
    client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(
    version="1", strict=True, deprecation_errors=True))
    # end example code here
except Exception as e:
    raise Exception(
        "Erro: ", e)

def define_senha( senha):
    senha = generate_password_hash(senha)
    return senha

def verifica_senha(senha, senha_hash):
    return check_password_hash(senha, senha_hash)



def ler_usuarios():
    # Selecionar banco de dados e coleção
    db = client["brassaco"]
    user = db["funcionarios"]
    # Buscar todos os documentos
    result = user.find()
    return list(result)
    


def criar_usuario(nome, email, senha, loja, adm=False):   
    # Selecionar banco de dados e coleção
    db = client["brassaco"]
    user = db["funcionarios"]
    result = user.insert_one({
        "nome": nome,
        "email": email,
        "password": define_senha(senha),
        "created_at": datetime.now(),
        "adm": adm,
        "loja": loja,
    })
    print(result.inserted_id)



def registrar(id, tipo):   
    # Selecionar banco de dados e coleção
    db = client["brassaco"]
    collection = db["funcionarios"]
    filter = {"_id": ObjectId(id)}
    # tz = timezone(timedelta(hours=-3))  # Brasília Time (UTC-3)
    # three_hours_ago_tz = current_time_tz - timedelta(hours=3)

    # current_time_tz = datetime.now(tz)
    # print(three_hours_ago_tz)
    now = datetime.now()
    three_hours_ago = now.replace(hour=now.hour - 3)

    update_data = {
    "$push": {
        "ponto": {  # Campo que contém o array
        "registro": three_hours_ago,
        "tipo": tipo,
        }    
            }   
    }
    result = collection.update_one(filter, update_data, upsert=True)   

def alterar_usuario(id, **kwargs):   
    # Selecionar banco de dados e coleção
    db = client["brassaco"]
    user = db["funcionarios"]
    filtro = {"_id": ObjectId(id)}

    atualizacao = {"$set": {}}
    for key, value in kwargs.items():
        if key == "password":
            atualizacao["$set"][key] = define_senha(value) # Hashes the password before updating
        else:
            atualizacao["$set"][key] = value  # Add other fields to the $set operator

    resultado = user.update_one(filtro, atualizacao)
    
    print(kwargs)

def apagar_usuario(id):
    db = client["brassaco"]
    user = db["funcionarios"]
    filtro = {"_id": ObjectId(id)}
    user.delete_one(filtro)

def trocar_senha(id, senha):
    db = client["brassaco"]
    user = db["funcionarios"]

    filtro = {"_id": ObjectId(id)}
    atualizacao = {"$set": {"password": define_senha(senha)}}
    user.update_one(filtro, atualizacao)

# registrar('67b86d93dd21965649fb3455', 'volta_almoco')    
# criar_usuario('Teste', 'marcio@gmail.com', 'teste', 'QI') 

    
