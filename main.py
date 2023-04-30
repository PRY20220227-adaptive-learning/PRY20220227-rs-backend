from api.users import router as users_router
from api.predictions import router as predictions_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import Base, Database

app = FastAPI(title="Recommender System API",
              version="1.0",
              openapi_url="/api/v1/openapi.json",
              docs_url="/api/v1/docs",
              )

db = Database()
engine = db.get_db_connection()

app.include_router(predictions_router,
                   prefix="/predictions", tags=["Predictions"])
app.include_router(users_router, prefix="/users", tags=["Users"])

origins = [
    # CLIENT_ORIGIN_URI,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print("Connected to database")


@app.on_event("shutdown")
def shutdown():
    print("Disconnected from database")


@app.get('/healthchecker', tags=["Healthchecker"])
def healthchecker():
    return {'message': 'System is active'}
