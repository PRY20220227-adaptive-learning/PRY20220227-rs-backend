from typing import List
from fastapi import APIRouter, Depends, HTTPException
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
    'A few/A little': 9,
    'Be going to': 2,
    'Can/Can\'t': 6,
    'Comparative adjectives': 5,
    'Comparative/Superlative': 10,
    'Could/Couldn\'t': 7,
    'Modal verbs': 11,
    'Past simple': 13,
    'Present continuous': 1,
    'Present simple': 0,
    'Quantifiers': 12,
    'Shall': 3,
    'Should/Shouldn\'t': 14,
    'Superlatives adjectives': 8,
    'Too/Enough': 15,
    'Verb to be': 4,
    'Want/Need/Would': 16
}

# Definir el número total de categorías en el modelo
n_categories = len(category_codes)


@router.post('/predict/student/{id}')
def predict_resources(input_data: InputData, id: int, db: Session = Depends(database.get_db_session)):

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

    # Agregar columnas para los otros valores posibles de knowledge_level
    for col in [f'knowledge_level_{level}' for level in ['Avanzado', 'Intermedio', 'Principiante']]:
        if col not in df.columns:
            df[col] = 0

    # Agregar columnas para los otros valores posibles de learning_style
    for col in [f'learning_style_{style}' for style in ['Auditivo', 'Kinestésico', 'Read/Write', 'Visual']]:
        if col not in df.columns:
            df[col] = 0

    # Convertir la columna "subject" a su valor ordinal correspondiente
    df['subject'] = df['subject'].map(category_codes).fillna(-1)

    print("sub", df)

    df = df.reindex(columns=['mark', 'subject', 'knowledge_level_Avanzado', 'knowledge_level_Intermedio', 'knowledge_level_Principiante',
                    'learning_style_Auditivo', 'learning_style_Kinestésico', 'learning_style_Read/Write', 'learning_style_Visual'])

    print("prd", df)

    # Hacer la predicción
    prediction = model.predict(df)

    # crear una instancia de Recommendations
    recommendation = Recommendations(
        date=datetime.now().date(),
        url=prediction[0],
        topic=input_data.subject,
        student_id=id,
    )

    db.add(recommendation)
    db.commit()

    # Devolver la predicción
    return prediction[0]


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
