from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "production_pipeline.joblib"
)

pipeline = joblib.load(MODEL_PATH)
feature_names = pipeline.feature_names_in_.tolist()

app = FastAPI(title="UK Road Accident Severity Prediction")


class PredictionRequest(BaseModel):
    features: dict[str, float | None]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(request: PredictionRequest):
    missing = sorted(set(feature_names) - set(request.features))
    unexpected = sorted(set(request.features) - set(feature_names))

    if missing or unexpected:
        raise HTTPException(
            status_code=422,
            detail={
                "missing_features": missing,
                "unexpected_features": unexpected,
            },
        )

    data = pd.DataFrame(
        [request.features],
        columns=feature_names,
        dtype=float,
    )

    prediction = int(pipeline.predict(data)[0])
    probabilities = pipeline.predict_proba(data)[0]

    return {
        "severity_code": prediction,
        "probabilities": {
            str(int(label)): float(probability)
            for label, probability in zip(
                pipeline.classes_, probabilities
            )
        },
    }