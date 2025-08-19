from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
from datetime import datetime
from passlib.context import CryptContext
import re
from pydantic import EmailStr


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB connection with fallback
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')

# In-memory storage for when MongoDB is not available
in_memory_users = {}
in_memory_status_checks = []

# Initialize MongoDB variables
client = None
db = None
mongo_available = False

# Only try to connect to MongoDB if explicitly configured
if mongo_url and db_name:
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        db = client[db_name]
        mongo_available = True
        logging.info(f"Connected to MongoDB at {mongo_url}")
    except Exception as e:
        logging.warning(f"Could not connect to MongoDB: {e}")
        mongo_available = False
        client = None
        db = None
        logging.info("Using in-memory storage for development")
else:
    logging.info("MongoDB not configured, using in-memory storage for development")

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_id: str
    money_given: float = 0.0
    total_spent: float = 0.0
    orders: List[dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerCreate(BaseModel):
    name: str
    money_given: Optional[float] = 0.0
    total_spent: Optional[float] = 0.0
    orders: Optional[List[dict]] = []

class CustomerUpdate(BaseModel):
    money_given: Optional[float] = None
    total_spent: Optional[float] = None
    orders: Optional[List[dict]] = None

class CustomerResponse(BaseModel):
    id: str
    name: str
    money_given: float
    total_spent: float
    orders: List[dict]
    created_at: datetime
    updated_at: datetime

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    pin: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(BaseModel):
    email: EmailStr
    pin: str
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError('Invalid email format')
        return v

class UserSignIn(BaseModel):
    email: EmailStr
    pin: str
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", v):
            raise ValueError('Invalid email format')
        return v

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime
    updated_at: datetime

# Password utilities
def hash_pin(pin: str) -> str:
    return pwd_context.hash(pin)

def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    return pwd_context.verify(plain_pin, hashed_pin)

# User routes
@api_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    try:
        if mongo_available:
            # Check if user already exists
            existing_user = await db.users.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Create new user
            user_dict = user_data.dict()
            user_dict["pin"] = hash_pin(user_data.pin)  # Hash the PIN
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            
            result = await db.users.insert_one(user_dict)
            user_dict["id"] = str(result.inserted_id)
        else:
            # Use in-memory storage
            if user_data.email in in_memory_users:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            user_dict = user_data.dict()
            user_dict["pin"] = hash_pin(user_data.pin)  # Hash the PIN
            user_dict["created_at"] = datetime.utcnow()
            user_dict["updated_at"] = datetime.utcnow()
            user_dict["id"] = str(uuid.uuid4())
            
            # Store in memory
            in_memory_users[user_data.email] = user_dict
        
        # Return user without PIN
        return UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            created_at=user_dict["created_at"],
            updated_at=user_dict["updated_at"]
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.post("/users/signin", response_model=UserResponse)
async def signin_user(user_data: UserSignIn):
    try:
        if mongo_available:
            # Find user by email
            user = await db.users.find_one({"email": user_data.email})
            if not user:
                raise HTTPException(status_code=401, detail="Invalid email or PIN")
            
            # Verify PIN
            if not verify_pin(user_data.pin, user["pin"]):
                raise HTTPException(status_code=401, detail="Invalid email or PIN")
        else:
            # Use in-memory storage
            if user_data.email not in in_memory_users:
                raise HTTPException(status_code=401, detail="Invalid email or PIN")
            
            user = in_memory_users[user_data.email]
            
            # Verify PIN
            if not verify_pin(user_data.pin, user["pin"]):
                raise HTTPException(status_code=401, detail="Invalid email or PIN")
        
        # Return user without PIN
        return UserResponse(
            id=str(user.get("_id", user.get("id"))),
            email=user["email"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error signing in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/users/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    try:
        if mongo_available:
            user = await db.users.find_one({"email": email})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            # Use in-memory storage
            if email not in in_memory_users:
                raise HTTPException(status_code=404, detail="User not found")
            user = in_memory_users[email]
        
        # Return user without PIN
        return UserResponse(
            id=str(user.get("_id", user.get("id"))),
            email=user["email"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/users", response_model=List[UserResponse])
async def get_all_users():
    try:
        if mongo_available:
            users = await db.users.find().to_list(1000)
        else:
            # Use in-memory storage
            users = list(in_memory_users.values())
        
        return [
            UserResponse(
                id=str(user.get("_id", user.get("id"))),
                email=user["email"],
                created_at=user["created_at"],
                updated_at=user["updated_at"]
            ) for user in users
        ]
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}")
        return []

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World from BABS10 API"}

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mongo_available": mongo_available,
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    if not mongo_available:
        return {"error": "Database not available"}
    
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    if not mongo_available:
        return []
    
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Customer routes
@api_router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate, user_id: str = None):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if mongo_available:
            # Check if customer already exists for this user
            existing_customer = await db.customers.find_one({
                "name": customer_data.name,
                "user_id": user_id
            })
            if existing_customer:
                raise HTTPException(status_code=400, detail="Customer with this name already exists for this user")
            
            # Create new customer
            customer_dict = customer_data.dict()
            customer_dict["user_id"] = user_id
            customer_dict["created_at"] = datetime.utcnow()
            customer_dict["updated_at"] = datetime.utcnow()
            
            result = await db.customers.insert_one(customer_dict)
            customer_dict["id"] = str(result.inserted_id)
        else:
            # Use in-memory storage
            customer_key = f"{user_id}_{customer_data.name}"
            if customer_key in in_memory_customers:
                raise HTTPException(status_code=400, detail="Customer with this name already exists for this user")
            
            customer_dict = customer_data.dict()
            customer_dict["user_id"] = user_id
            customer_dict["created_at"] = datetime.utcnow()
            customer_dict["updated_at"] = datetime.utcnow()
            customer_dict["id"] = str(uuid.uuid4())
            
            # Store in memory
            in_memory_customers[customer_key] = customer_dict
        
        # Return customer
        return CustomerResponse(
            id=customer_dict["id"],
            name=customer_dict["name"],
            money_given=customer_dict["money_given"],
            total_spent=customer_dict["total_spent"],
            orders=customer_dict["orders"],
            created_at=customer_dict["created_at"],
            updated_at=customer_dict["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/customers", response_model=List[CustomerResponse])
async def get_customers_by_user(user_id: str):
    try:
        if mongo_available:
            customers = await db.customers.find({"user_id": user_id}).to_list(1000)
        else:
            # Use in-memory storage
            customers = [
                customer for customer in in_memory_customers.values() 
                if customer["user_id"] == user_id
            ]
        
        return [
            CustomerResponse(
                id=customer["id"],
                name=customer["name"],
                money_given=customer["money_given"],
                total_spent=customer["total_spent"],
                orders=customer["orders"],
                created_at=customer["created_at"],
                updated_at=customer["updated_at"]
            ) for customer in customers
        ]
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        return []

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str, user_id: str = None):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if mongo_available:
            result = await db.customers.delete_one({
                "_id": customer_id,
                "user_id": user_id
            })
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Customer not found")
        else:
            # Use in-memory storage
            customer_key = None
            for key, customer in in_memory_customers.items():
                if customer["id"] == customer_id and customer["user_id"] == user_id:
                    customer_key = key
                    break
            
            if customer_key:
                del in_memory_customers[customer_key]
            else:
                raise HTTPException(status_code=404, detail="Customer not found")
        
        return {"message": "Customer deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: str, customer_update: CustomerUpdate, user_id: str = None):
    try:
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        if mongo_available:
            # Find and update customer
            update_data = customer_update.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db.customers.update_one(
                {"_id": customer_id, "user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            # Get updated customer
            updated_customer = await db.customers.find_one({"_id": customer_id})
        else:
            # Use in-memory storage
            customer_key = None
            for key, customer in in_memory_customers.items():
                if customer["id"] == customer_id and customer["user_id"] == user_id:
                    customer_key = key
                    break
            
            if not customer_key:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            # Update customer in memory
            customer = in_memory_customers[customer_key]
            update_data = customer_update.dict(exclude_unset=True)
            customer.update(update_data)
            customer["updated_at"] = datetime.utcnow()
            
            updated_customer = customer
        
        # Return updated customer
        return CustomerResponse(
            id=updated_customer["id"],
            name=updated_customer["name"],
            money_given=updated_customer.get("money_given", 0.0),
            total_spent=updated_customer.get("total_spent", 0.0),
            orders=updated_customer.get("orders", []),
            created_at=updated_customer["created_at"],
            updated_at=updated_customer["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Initialize in-memory storage for customers
in_memory_customers = {}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
