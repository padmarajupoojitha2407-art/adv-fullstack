from sqlalchemy import Integer, String, Column, create_engine, Float, Date, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta, timezone
import jwt

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

WAREHOUSE_MODULES = ["Packages", "Dispatch", "Analytics"]




USERNAME = "Poojitha"
PASSWORD = "123"


ACCESS_TOKEN_EXPIRY = 1 #mins
REFRESH_TOKEN_EXPIRY = 7*24*60 #mins (7 days)
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"


Base = declarative_base()


class Packages(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(Date)
    status = Column(String, default="pending")
    dispatch_batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable=True)

class DispatchBatches(Base):
    __tablename__ = "dispatch_batches"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status = Column(String, default="pending")
    dispatch_date = Column(Date, nullable=True)

Base.metadata.create_all(engine)

def package_details(package):
    return {
        "id": package.id,
        "package_name": package.package_name,
        "destination": package.destination,
        "weight": package.weight,
        "arrival_date": str(package.arrival_date),
        "status": package.status,
        "dispatch_batch_id": package.dispatch_batch_id
    }

# E1
def add_package(package_name, destination, weight, arrival_date):
    session = Session(engine)
    package = Packages(
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=date.fromisoformat(arrival_date),
        status="pending"
    )
    session.add(package)
    session.commit()
    session.refresh(package)
    response = package_details(package)
    session.close()
    return response

# E2
def get_package(package_id):
    session = Session(engine)
    package = session.get(Packages, package_id)
    if package is None:
        session.close()
        return None
    response = package_details(package)
    session.close()
    return response

# E3
def update_package(package_id, data):
    session = Session(engine)
    package = session.get(Packages, package_id)
    if package is None:
        session.close()
        return "not_found"
    if package.status == "dispatched":
        session.close()
        return "already_dispatched"
    if package.dispatch_batch_id is not None:
        session.close()
        return "already_assigned"
    if "arrival_date" in data:
        data["arrival_date"] = date.fromisoformat(data["arrival_date"])
    for key, value in data.items():
        setattr(package, key, value)
    session.commit()
    response = package_details(package)
    session.close()
    return response

# E4
def delete_package(package_id):
    session = Session(engine)
    package = session.get(Packages, package_id)
    if package is None:
        session.close()
        return "not_found"
    if package.status == "dispatched":
        session.close()
        return "already_dispatched"
    session.delete(package)
    session.commit()
    session.close()
    return "deleted"

# E5
def get_all_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)
    packages = session.query(Packages)
    if destination:
        packages = packages.filter(Packages.destination == destination)
    if status:
        packages = packages.filter(Packages.status == status)
    if arrival_date:
        arrival_date = date.fromisoformat(arrival_date)
        packages = packages.filter(Packages.arrival_date == arrival_date)
    response = [package_details(p) for p in packages.all()]
    session.close()
    return response





























def verify_login(username, password):
    if username ==USERNAME and password == PASSWORD:
        access_token = create_token(username=username, token_type="access")
        refresh_token = create_token(username=username, token_type="refresh")
        return {"access_token": access_token, "refresh_token": refresh_token}
    return None
        
def create_token(username, token_type):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload ={
        "username": username,
        "token_type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=time)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token, token_type):
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])

    except:
        return False
    if payload["token_type"] == token_type:
        return payload["username"]
    
    return False

    