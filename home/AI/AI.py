# Импорт библиотек
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
from xgboost import XGBClassifier
import joblib
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

YEARS = 20
diseases = ['stroke', 'arrhythmia', 'ischemic_heart_disease', 'hypertension', 'heart_failure']
FEATURES = ['age', 'sex', 'height', 'weight', 'activity_level', 'sleep_hours', 'smoking', 'alcohol', 'stress_level', 'bmi']

BASE_DIR = Path(__file__).resolve().parent
models = {}
for disease in diseases:
    models[disease] = []
    for year in range(1, YEARS + 1):
        model_path = BASE_DIR / 'models' / f'{disease}_year{year}.joblib'
        models[disease].append(joblib.load(model_path))

scaler = joblib.load(BASE_DIR / 'models' / 'scaler.joblib')

def calculate_bmi(weight, height):
    return weight / ((height / 100) ** 2)

def predict_risks(user_data: dict) -> dict:
    df = pd.DataFrame([user_data])
    df['bmi'] = calculate_bmi(df['weight'], df['height'])
    X = scaler.transform(df[FEATURES])

    results = {}
    for disease in diseases:
        probs = []
        for model in models[disease]:
            prob = model.predict_proba(X)[0][1]
            probs.append(round(prob * 100, 2))
        results[disease] = probs

    return results

YEARS = 20
DISEASES = ['stroke', 'arrhythmia', 'ischemic_heart_disease', 'hypertension', 'heart_failure']

np.random.seed(42)
n_samples = 10000
ages = np.random.randint(20, 60, n_samples)
sexes = np.random.randint(0, 2, n_samples)
heights = np.random.normal(170, 10, n_samples)
weights = np.random.normal(70, 15, n_samples)
bmis = weights / (heights / 100) ** 2

activity_level = np.clip((np.random.normal(3, 1, n_samples) - 0.02 * ages), 1, 5).astype(int)
sleep_hours = np.clip(np.random.normal(7 - 0.01 * ages + 0.1 * activity_level, 1), 4, 9)
smoking = (np.random.rand(n_samples) < (0.35 - 0.003 * ages)).astype(int)
alcohol = (np.random.rand(n_samples) < (0.4 - 0.002 * ages)).astype(int)
stress_level = np.clip(
    np.random.normal(3 + 0.01 * smoking + 0.01 * alcohol - 0.05 * activity_level, 1), 1, 5
).astype(int)

X = pd.DataFrame({
    'age': ages,
    'sex': sexes,
    'height': heights,
    'weight': weights,
    'activity_level': activity_level,
    'sleep_hours': sleep_hours,
    'smoking': smoking,
    'alcohol': alcohol,
    'stress_level': stress_level,
    'bmi': bmis
})

Y = {}
for disease in DISEASES:
    Y[disease] = pd.DataFrame()
    for year in range(YEARS):
        base_risk = 0.01 + 0.005 * year
        risk = (
            0.002 * (X['age'] + year) +
            0.015 * X['bmi'] +
            0.03 * X['smoking'] +
            0.02 * X['alcohol'] +
            0.01 * (6 - X['sleep_hours']) +
            0.02 * (X['stress_level'] - 2.5) -
            0.01 * (X['activity_level'] - 3)
        ) / 100 + base_risk
        risk = np.clip(risk, 0, 1)
        Y[disease][f'y{year+1}'] = np.random.binomial(1, risk)

features = ['age', 'sex', 'height', 'weight', 'activity_level', 'sleep_hours', 'smoking', 'alcohol', 'stress_level', 'bmi']
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[features])

models = {}
for disease in DISEASES:
    models[disease] = []
    for year in range(YEARS):
        y = Y[disease][f'y{year+1}']
        x_train, x_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

        model = XGBClassifier(eval_metric='logloss')
        calibrated = CalibratedClassifierCV(model, method='sigmoid', cv=3)
        calibrated.fit(x_train, y_train)

        preds = calibrated.predict_proba(x_test)[:, 1]
        score = brier_score_loss(y_test, preds)
        print(f'{disease} - year {year+1}: Brier score = {score:.4f}')

        models[disease].append(calibrated)

os.makedirs('models', exist_ok=True)
for disease in DISEASES:
    for year in range(YEARS):
        joblib.dump(models[disease][year], f'models/{disease}_year{year+1}.joblib')

joblib.dump(scaler, 'models/scaler.joblib')
