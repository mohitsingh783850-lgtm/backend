from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from .model import TalentRequest, JobApplication, ContactMessage, UserLogin, UserRegister, JobApplicationSchema
from .database import get_collection, db, applications_collection
from .utils.auth_helpers import hash_password, verify_password, create_access_token
import os
from bson import ObjectId
from datetime import datetime

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "welcome to my backend api!", "status": "running"}

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Collections
requests_collection = get_collection("requests")
messages_collection = get_collection("contact_messages")
users_collection = get_collection("users")

# 1. Talent Request Route
@app.post("/submit", tags=["talent"])
def submit_talent_request(payload: TalentRequest):
    try:
        # payload.model_dump() now automatically includes req_age, req_education, etc.
        result = requests_collection.insert_one(payload.model_dump())
        return {"message": "Success", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

# # 2. Job Application Route
# @app.post("/apply")
# def apply_for_job(
#     first_name: str = Form(...),
#     last_name: str = Form(...),
#     email: str = Form(...),
#     phone: str = Form(...),
#     address: str = Form(...),
#     sex: str = Form(None),
#     age: int = Form(None),
#     education: str = Form(...),
#     skills: str = Form(...),
#     experience: str = Form(...),
#     qualities: str = Form(...),
#     additional_info: str = Form(None),
#     photo: UploadFile = File(...)
# ):
#     try:
#         file_location = f"uploads/{photo.filename}"
#         with open(file_location, "wb+") as file_object:
#             file_object.write(photo.file.read())

#         application_data = {
#             "first_name": first_name,
#             "last_name": last_name,
#             "email": email,
#             "phone": phone,
#             "address": address,
#             "sex": sex,
#             "age": age,
#             "education": education,
#             "skills": skills,
#             "experience": experience,
#             "qualities": qualities,
#             "additional_info": additional_info,
#             "photo_path": file_location,
#             "status": "pending"
#         }

#         db.applications.insert_one(application_data)
#         return {"message": "Application Submitted!"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# 3. Contact Message Route
@app.post("/contact")
def send_contact_message(data: ContactMessage): 
    try:
        result = messages_collection.insert_one(data.model_dump())
        return {"status": "success", "msg": "Message sent to the team!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. User Registration Route
@app.post("/register")
def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user.password)
    users_collection.insert_one(user_dict)
    return {"message": "User created successfully"}

# 5. User Login Route
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

@app.post("/submit-talent", tags=["talent"]) # Renamed to be more specific
def submit_talent_request(payload: TalentRequest):
    try:
        # Convert Pydantic model to a dictionary for MongoDB
        talent_data = payload.model_dump()
        
        # Insert into the "requests" collection
        result = requests_collection.insert_one(talent_data)
        
        return {
            "status": "success",
            "message": "Talent request received and saved!",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        # If MongoDB fails or data is bad, this will tell us why
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Database insertion failed")

@app.post("/api/applications", status_code=status.HTTP_201_CREATED)
def submit_application(application: JobApplicationSchema): # Dropped 'async' here
    try:
        # Convert Pydantic model data to a Python dictionary
        application_dict = application.model_dump()
        
        # Add server metadata
        application_dict["createdAt"] = datetime.utcnow()
        application_dict["status"] = "pending"
        
        # Synchronous insert into MongoDB (no 'await' needed)
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