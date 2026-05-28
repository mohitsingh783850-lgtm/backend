from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from .model import TalentRequest, JobApplication, ContactMessage, UserLogin, UserRegister, JobApplicationSchema
from .database import get_collection, db, applications_collection
from .utils.auth_helpers import hash_password, verify_password, create_access_token
import os
from bson import ObjectId
from datetime import datetime

app = FastAPI()

# 1. FIXED: CORS configuration (Added both localhost and 127.0.0.1 variants)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "welcome to my backend api!", "status": "running"}

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Collections
requests_collection = get_collection("requests")
messages_collection = get_collection("contact_messages")
users_collection = get_collection("users")


# 2. Talent Request Routes (FIXED: Cleaned up duplicates)
@app.post("/submit", tags=["talent"])
def submit_talent_legacy(payload: TalentRequest):
    try:
        result = requests_collection.insert_one(payload.model_dump())
        return {"message": "Success", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-talent", tags=["talent"]) 
def submit_talent_request_new(payload: TalentRequest): # FIXED: Changed function name to be unique
    try:
        talent_data = payload.model_dump()
        result = requests_collection.insert_one(talent_data)
        return {
            "status": "success",
            "message": "Talent request received and saved!",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database insertion failed")

@app.get("/get-talent", tags=["talent"])
def get_talent():
    try:
        cursor = requests_collection.find()
        allTalent = []
        for talent in cursor:
            talent["_id"] = str(talent["_id"])
            allTalent.append(talent)
        return {
            "status": "get all talent successfully",
            "data": allTalent 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-talent/{talent_id}", tags=["talent"])
def get_talent_by_id(talent_id: str):
    try:
        query_id = ObjectId(talent_id)
        talent = requests_collection.find_one({"_id": query_id })
        
        if not talent:
            raise HTTPException(status_code=404, detail="Talent not found")

        talent["_id"] = str(talent["_id"])
        return {
            "status": "get talent detail successfully",
            "data": talent 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. Contact Message Route
@app.post("/contact")
def send_contact_message(data: ContactMessage): 
    try:
        result = messages_collection.insert_one(data.model_dump())
        return {"status": "success", "msg": "Message sent to the team!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. User Authentication Routes
@app.post("/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user.password)
    users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": str(db_user["_id"]), "email": db_user["email"]})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "name": db_user.get("name"),
            "email": db_user.get("email")
        }
    }


# 5. Job Application Route
@app.post("/api/applications", status_code=status.HTTP_201_CREATED)
def submit_application(application: JobApplicationSchema): 
    try:
        application_dict = application.model_dump()
        application_dict["createdAt"] = datetime.utcnow()
        application_dict["status"] = "pending"
        
        result = applications_collection.insert_one(application_dict)
        return {
            "message": "Application submitted successfully!",
            "applicationId": str(result.inserted_id)
        }
    except Exception as e:
        print(f"Database insertion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error. Could not store application."
        )