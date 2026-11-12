from fastapi import FastAPI, HTTPException, Body, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

import function


app = FastAPI()


app.add_middleware(
     CORSMiddleware,
     allow_origins=["http://localhost:5173"], 
     allow_methods=["*"], 
     allow_headers=["*"] 
)


# E1 - Register Package
@app.post("/packages")
def add_package(package_name: str, destination: str,
                weight: float, arrival_date: date):
    if weight <= 0: 
        raise HTTPException(status_code=422, detail="Invalid weight")

    return function.add_package(
        package_name, destination, weight, arrival_date
    )



# E2 - Get Specific Package
@app.get("/packages/{package_id}")
def get_package(package_id: int, token = Header(None)):
    username = function.verify_token(token=token)
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    response = function.get_package(package_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return response


# E3 - Update Package
@app.patch("/packages/{package_id}")
def update_package(package_id: int, package_name: str = None,
                   destination: str = None, weight: float = None,
                   arrival_date: date = None):

    result = function.update_package(
        package_id, package_name, destination, weight, arrival_date
    )

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")

    return result


# E4 - Delete Package
@app.delete("/packages/{package_id}")
def delete_package(package_id: int):

    result = function.delete_package(package_id)

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")

    if result == "dispatched":
        raise HTTPException(status_code=400, detail="Package already dispatched")

    return result


# E5 - Filter Packages
@app.get("/packages")
def filter_packages(destination: str = None, status: str = None):

    return function.filter_packages(destination, status)









































@app.post("/login")
def login (username: str, password: str):
    token = function.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

@app.post("/refresh")
def refresh_token(refresh_token = Header(None)):
    username = function.verify_token(token=refresh_token, token_type="refresh")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expired refresh token")
    access_token = function.create_token(username=username, token_type="access")
    return {"access_token": access_token}


