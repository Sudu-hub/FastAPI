from fastapi import FastAPI, Path, HTTPException
import json

app = FastAPI()

@app.get('/') #1st endpoint
def home():
    return {'Message':'Hello FastApi'}

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
    
    return data
@app.get('/about')
def about():
    return {'message':'This is a fastapi practice app'}

@app.get('/view')
def veiw_data():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def patient_data(patient_id: str = Path(..., description='ID of the patient in the db', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(status_code=404, detail='patient not found')