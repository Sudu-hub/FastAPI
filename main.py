from fastapi import FastAPI, Path,Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    
    # add the field whose support to create patient class
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='name of the patient',)]
    city: Annotated[str, Field(..., description='City where the patient if living')]
    age:Annotated[int, Field(..., gt=0, lt=120, description='Add age between 0 and 120')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the parient')]
    height: Annotated[float, Field(..., gt=0, description='hight of the patient in meteres')]
    weight: Annotated[float, Field(..., description='weight of the patient in kgs')]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height ** 2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        
        if self.bmi < 18.5:
            return 'Underweight'
        
        elif self.bmi < 25:
            return 'Normal'
        
        elif self.bmi < 30:
            return 'Overweight'
        
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age:Annotated[Optional[int], Field(default=None)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float],Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    
    

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)

    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)
        
@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get('/veiw')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='ID of the patient in the DB', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(status_code=404, detail='Patient not found')

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description='sort on the basis of height and weight or bmi'), order: str = Query('asc', description='sort in asc or desc order')):
    
    valid_fields = {'height', 'weight', 'bmi'}
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail=f'Invalid field select between asc and desc')
    
    data = load_data()
    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    
    #load existing data
    data = load_data()
    
    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    
    # new patient add to the database
    # convert pidantic object into dictionary to add the patient id
    # model_dump function convert pydantic object into dictionary
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    # save into the json file
    save_data(data)
    
    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient is not found')
    
    existing_patient_info = data[patient_id]
    upadated_patient_info = patient_update.model_dump(exclude_unset=True)
    
    for key, value in upadated_patient_info.items():
        existing_patient_info[key] = value
    
    # existing_patient_info -> pydantic object -> updated bmi + verdict -> convert this pydantic object into dict -> dict
    existing_patient_info['id'] = patient_id
    patient_pydantic = Patient(**existing_patient_info)
    
    # pydantic object -> dict
    
    patient_pydantic_info = patient_pydantic.model_dump(exclude='id')
    
    data[patient_id] = existing_patient_info
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message':'patient updated'})
    
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message':'patient deleted'})
    