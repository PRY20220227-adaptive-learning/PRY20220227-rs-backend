from typing import List
from fastapi import APIRouter, Depends, HTTPException
import numpy as np
from database.connection import Database
from models.recommendation import Recommendations
from schemas.input_data import InputData
from datetime import datetime
from sqlalchemy.orm import Session


import joblib
import pandas as pd

from schemas.recommendation import RecommendationResponse

router = APIRouter()
database = Database()
model = joblib.load('random_forest_model.joblib')


# Definir diccionario de correspondencias
category_codes = {
    'A few/A little': 0,
    'Be going to': 1,
    'Can/Can\'t': 2,
    'Comparative adjectives': 3,
    'Comparative/Superlative': 4,
    'Could/Couldn\'t': 5,
    'Modal verbs': 6,
    'Past simple': 7,
    'Present continuous': 8,
    'Present simple': 9,
    'Quantifiers': 10,
    'Shall': 11,
    'Should/Shouldn\'t': 12,
    'Superlatives adjectives': 13,
    'Too/Enough': 14,
    'Verb to be': 15,
    'Want/Need/Would': 16
}

# Definir el número total de categorías en el modelo
n_categories = len(category_codes)


@router.post('/predict/student/{id}')
def predict_resources(input_data: InputData, id: int, db: Session = Depends(database.get_db_session)):

    # Asegurar que mark es float
    if not isinstance(input_data.mark, float):
        input_data.mark = float(input_data.mark)

    # Preprocesar los datos de entrada
    df = pd.DataFrame({
        'mark': [input_data.mark],
        'knowledge_level': [input_data.knowledge_level],
        'learning_style': [input_data.learning_style],
        'subject': [input_data.subject]
    })

    # Convertir las variables categóricas a numéricas usando one-hot encoding
    df = pd.get_dummies(df, columns=['knowledge_level', 'learning_style'])

    # Agregar columnas para los otros valores posibles de knowledge_level y  learning_style
    for col in [f'knowledge_level_{level}' for level in ['Avanzado', 'Intermedio', 'Principiante']]:
        if col not in df.columns:
            df[col] = 0

    for col in [f'learning_style_{style}' for style in ['Auditivo', 'Kinestésico', 'Read/Write', 'Visual']]:
        if col not in df.columns:
            df[col] = 0

    # Reaordenar las columnas del dataframe para que coincida con el modelo
    df = df.reindex(columns=['mark', 'subject', 'knowledge_level_Avanzado', 'knowledge_level_Intermedio', 'knowledge_level_Principiante',
                    'learning_style_Auditivo', 'learning_style_Kinestésico', 'learning_style_Read/Write', 'learning_style_Visual'])

    # Hacer la predicción
    probabilities = model.predict_proba(df)

    # Obtener las etiquetas correspondientes a las probabilidades más altas
    labels = [model.classes_[
        i] if i is not None else None for i in np.argsort(-probabilities[0])[:4]]

    # Convertir las etiquetas predichas en URLs
    urls = [label for label in labels]

    # Convertir el diccionario en una lista de tuplas para hallar el nombre del tema
    category_codes_list = list(category_codes.items())

    subject = None
    for category, code in category_codes_list:
        if code == int(input_data.subject):
            subject = category
            break

    # Almacenar cada URL en la base de datos
    for url in urls:
        recommendation = Recommendations(
            date=datetime.now().date(),
            url=url,
            topic=subject,
            student_id=id,
        )
        db.add(recommendation)

    db.commit()

    # Devolver las URLs predichas
    return urls


@router.get('/history/user/{id}', response_model=List[RecommendationResponse])
def get_resources_by_user_id(id: int, db: Session = Depends(database.get_db_session)):
    recommendations = db.query(Recommendations).filter(
        Recommendations.student_id == id).all()
    if not recommendations:
        raise HTTPException(
            status_code=404, detail=f"No se encontraron recomendaciones para el estudiante con id {id}")
    response = []
    for recommendation in recommendations:
        response.append(RecommendationResponse(date=str(
            recommendation.date), url=recommendation.url, topic=recommendation.topic))
    return response
