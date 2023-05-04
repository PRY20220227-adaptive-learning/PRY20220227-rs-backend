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
    'A few/A little': '0',
    'Be going to': '1',
    'Can/Can\'t': '2',
    'Comparative adjectives': '3',
    'Comparative/Superlative': '4',
    'Could/Couldn\'t': '5',
    'Modal verbs': '6',
    'Past simple': '7',
    'Present continuous': '8',
    'Present simple': '9',
    'Quantifiers': '10',
    'Shall': '11',
    'Should/Shouldn\'t': '12',
    'Superlatives adjectives': '13',
    'Too/Enough': '14',
    'Verb to be': '15',
    'Want/Need/Would': '16'
}

# Definir el número total de categorías en el modelo
n_categories = len(category_codes)


@router.post('/predict/student/{id}')
def predict_resources(input_data: InputData, id: int, db: Session = Depends(database.get_db_session)):

    # Definir umbral de probabilidad
    umbral_probabilidad = 0.15

    # Realizar las cuatro consultas al modelo con los valores de mark variados
    probabilidades1 = model.predict_proba(
        create_data_frame(input_data.mark + 2, input_data.knowledge_level, input_data.learning_style, input_data.subject))[0]
    probabilidades2 = model.predict_proba(
        create_data_frame(input_data.mark + 1, input_data.knowledge_level, input_data.learning_style, input_data.subject))[0]
    probabilidades3 = model.predict_proba(
        create_data_frame(input_data.mark - 1, input_data.knowledge_level, input_data.learning_style, input_data.subject))[0]
    probabilidades4 = model.predict_proba(
        create_data_frame(input_data.mark - 2, input_data.knowledge_level, input_data.learning_style, input_data. subject))[0]

    # Combinar las probabilidades de las cuatro consultas
    probabilidades = (probabilidades1 + probabilidades2 +
                      probabilidades3 + probabilidades4) / 4

    # Seleccionar las clases con una probabilidad mayor que el umbral
    seleccionadas = np.where(probabilidades > umbral_probabilidad)[0]
    etiquetas_seleccionadas = model.classes_[seleccionadas].tolist()

    # Guardar las recomendaciones
    save_recommendations(etiquetas_seleccionadas, id, input_data.subject, db)

    # Devolver las etiquetas seleccionadas
    return etiquetas_seleccionadas


def create_data_frame(mark: float, knowledge_level: str, learning_style: str, subject: str):

    # Asegurar que mark es float
    if not isinstance(mark, float):
        mark = float(mark)

    # Preprocesar los datos de entrada
    df = pd.DataFrame({
        'mark': [mark],
        'knowledge_level': [knowledge_level],
        'learning_style': [learning_style],
        'subject': [subject]
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
    return df


def save_recommendations(urls: list, id: int, subject: str, db: Session):

    # Convertir el diccionario en una lista de tuplas para hallar el nombre del tema
    category_codes_list = list(category_codes.items())

    # Encontrar el nombre del tema correspondiente al código recibido
    for category, code in category_codes_list:
        if code == subject:
            subject = category
            break

    # Verificar que el tema no sea nulo
    if subject is None:
        raise ValueError("El código del tema no es válido")

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
    return


@router.get('/history/user/{id}', response_model=List[RecommendationResponse])
def get_resources_by_user_id(id: int, db: Session = Depends(database.get_db_session)):
    recommendations = db.query(Recommendations).filter(
        Recommendations.student_id == id).order_by(Recommendations.date.desc()).all()
    if not recommendations:
        raise HTTPException(
            status_code=404, detail=f"No se encontraron recomendaciones para el estudiante con id {id}")
    response = []
    for recommendation in recommendations:
        response.append(RecommendationResponse(date=str(
            recommendation.date), url=recommendation.url, topic=recommendation.topic))
    return response
