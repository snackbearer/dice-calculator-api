from fastapi import FastAPI

from app.api import router


app = FastAPI(title="Dice Calculator API")
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Dice Calculator API"}
