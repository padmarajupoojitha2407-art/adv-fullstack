from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from pydantic import BaseModel, Field

import function


app = FastAPI()

USER_TYPE = ["admin", "manager", "staff"]

def check_role(token, allowed_roles):
    username = function.verify_token(
        token=token,
        token_type="access"
    )

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_type = function.get_user_role(token)

    if not user_type:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    if user_type not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )







class PackageCreate(BaseModel):
    package_name: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    weight: float = Field(gt=0)
    arrival_date: date


class PackageUpdate(BaseModel):
    package_name: str | None = Field(default=None, min_length=1)
    destination: str | None = Field(default=None, min_length=1)
    weight: float | None = Field(default=None, gt=0)
    arrival_date: date | None = None


class DispatchCreate(BaseModel):
    destination: str = Field(min_length=1)
    vehicle: str = Field(min_length=1)
    package_ids: list[int] = Field(min_length=1)


class UserIn(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    user_type: str 


app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:5173"], 
     allow_methods=["*"], 
     allow_headers=["*"] 
)


# E1 
@app.post("/packages")
def add_package(package: PackageCreate, token = Header(None)):
    check_role(token,["admin", "manager"])
    return function.add_package(
        package.package_name, package.destination, package.weight, package.arrival_date
    )



# E2 
@app.get("/packages/{package_id}")
def get_package(package_id: int, token = Header(None)):
    check_role(token,["admin", "manager", "staff"])
    response = function.get_package(package_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return response



# E3
@app.patch("/packages/{package_id}")
def update_package(package_id: int, package: PackageUpdate, token=Header(None)):

    check_role(token,["admin", "manager", "staff"])
    # only the fields the user actually sent
    result = function.update_package(package_id, package.model_dump(exclude_unset=True))

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "already_dispatched":
        raise HTTPException(status_code=400, detail="Package already dispatched")

    if result == "already_assigned":
        raise HTTPException(status_code=400, detail="Package already assigned")

    return result



# E4 
@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token = Header(None)):

    check_role(token,["admin", "manager"])

    result = function.delete_package(package_id)

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "already_dispatched":
        raise HTTPException(status_code=400, detail="Package already dispatched")

    return result


# E5 
@app.get("/packages")
def filter_packages(destination: str = None, status: str = None, token = Header(None)):

    check_role(token,["admin", "manager", "staff"])

    return function.filter_packages(destination, status)


# E6 
@app.get("/dispatches")
def get_dispatch(destination: str = None, vehicle: str = None,
                   status: str = None, token = Header(None)):

    check_role(token,["admin", "manager", "staff"])
    return function.get_dispatch(destination, vehicle, status)


#E7
@app.get("/analytics") 
def get_analytics(token = Header(None)):
    check_role(token,["admin", "manager", "staff"])
    return function.get_warehouse_statistics()


# E8 - Create Dispatch Batch
@app.post("/dispatches")
def add_dispatch(dispatch: DispatchCreate, token = Header(None)):

    check_role(token,["admin", "manager", "staff"])

    result = function.add_dispatch(dispatch.destination, dispatch.vehicle, dispatch.package_ids)

    if result == "not_found":
        raise HTTPException(
            status_code=404,
            detail="One or more packages not found"
        )

    if result == "already_dispatched":
        raise HTTPException(
            status_code=400,
            detail="One or more packages are already dispatched"
        )

    if result == "invalid_destination":
        raise HTTPException(
            status_code=400,
            detail="Package destination does not match dispatch destination"
        )

    return result







































#tokens
@app.post("/login")
def login (username, password):
    token = function.verify_login(username=username, password=password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

@app.post("/refresh")
def refresh_token(refresh_token = Header(None)):
    username = function.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expired refresh token")
    access_token = function.create_token(username=username, token_type="access")
    return {"access_token": access_token}


@app.post("/register")
def register_user(user: UserIn):
    if user.user_type not in USER_TYPE:
        raise HTTPException(status_code= 400, detail = "user_type must be admin , staff or manager")
    if function.register_User(username=user.username, password=user.password, user_type = user.user_type):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists:")


