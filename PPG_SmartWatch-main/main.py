# Registration Server Code
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field, EmailStr
import motor.motor_asyncio
import json
from bson import ObjectId
from typing import Optional, List

import os
import uvicorn

with open('creds_sample.json') as f:
    data = json.loads(f.read())
    MONGODB_URL = data['mongodb_creds'][0]['MONGODB_URL']


app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.college

# MongoDB stuff
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Main UserData Class
class UserData(BaseModel):
    id : PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name : str = Field(...)
    sensor_id : List = Field(...)
    pub_key: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "sensor_id": [1], 
                "pub_key": "cryptokey"
            }
        }

# Class with Optional Fields, only need to supply data that needs to be updated
class UpdateUserData(BaseModel):
    name: Optional[str]
    sensor_id: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "sensor_id": [1]
            }
        }

class SensorMeta(BaseModel):
    sensor_id: int
    SensorType: str


# Timeseries Data Collection
class TimeSeries(BaseModel):
    timeField: str = Field(...)
    metaField: SensorMeta = Field(...)
    granularity: str = Field(...)
    data: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "timeField": "timestamp",
                "metaField": {"10", "HeartBeat"},
                "granularity": "hours",
                "data": "encrypted_sensor_data"
            }
        }

# SensorData Collection
class SensorData(BaseModel):
    timeseries: TimeSeries

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        # schema_extra = {
        #     "example": {
        #         "timeField": "timestamp",
        #         "metaField": "metadata",
        #         "granularity": "hours"
        #     }
        # }


    
    


@app.get("/")
async def root():
    return {"message":"Hello World"}

# Create new user
@app.post("/userdata/", response_description="Adds new user", response_model=UserData)
async def save_userdata(data: UserData):
    # data_dict = data.dict()
    data = jsonable_encoder(data)
    new_user = await db["user"].insert_one(data)
    created_user = await db["user"].find_one({"_id": new_user.inserted_id})

    # data_dict.update({"data":data.data + " has been read"})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

# Create new sensor
@app.post("/sensordata/", response_description="Adds new sensor", response_model=SensorData)
async def save_userdata(data: SensorData):
    # data_dict = data.dict()
    data = jsonable_encoder(data)
    new_sensor = await db["sensor"].insert_one(data)
    created_user = await db["sensor"].find_one({"timeseries":{"metaField":{"sensor_id": data['timeseries']['metaField']['sensor_id']} }})

    # data_dict.update({"data":data.data + " has been read"})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)


# List User acc to id
# [INSECURE] Need to add checks to prevent random access via users
@app.get(
    "/sensordata/{id}/{timestamp}", response_description="Get sensor data", response_model=SensorData
)
async def show_student(id: str, timestamp:str):
    if (Sensor := await db["sensor"].find_one({"$and",{"metaField":{"sensor_id": id}}, {"timestamp":timestamp}})) is not None:
        print("Sensor Found")
        return Sensor
    print("Sensor Not Found")
    raise HTTPException(status_code=404, detail=f"Sensor {id} data at timestamp {timestamp} not found")

@app.put("/{id}", response_description="Update a user", response_model=UserData)
async def update_student(id: str, user: UpdateUserData = Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await db["user"].update_one({"_id": id}, {"$set": user})

        if update_result.modified_count == 1:
            if (
                updated_user := await db["user"].find_one({"_id": id})
            ) is not None:
                return updated_user

    if (existing_user := await db["user"].find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.delete("/{id}", response_description="Delete a user")
async def delete_student(id: str):
    delete_result = await db["user"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)