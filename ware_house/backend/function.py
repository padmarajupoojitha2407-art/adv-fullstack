from sqlalchemy import Integer, String, Column, create_engine, Float, Date, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import datetime, timedelta
import jwt

DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()

WAREHOUSE_MODULES = ["Packages", "Dispatch", "Analytics"]




USERNAME = "Poojitha"
PASSWORD = "123"


ACCESS_TOKEN_EXPIRY = 15 #* 60  # 15 minutes in seconds
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"




# Table 1: Packages
class Packages(Base):

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(Date)
    status = Column(String, default="pending")
    dispatch_id = Column(Integer, ForeignKey("dispatches.id"), nullable=True)


# Table 2: Dispatches
class Dispatches(Base):

    __tablename__ = "dispatches"

    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status = Column(String, default="pending")


Base.metadata.create_all(engine)




# E1 - Register Package

def add_package(package_name, destination, weight, arrival_date):

    session = Session(engine)

    package = Packages(
        package_name=package_name,
        destination=destination,
        weight=weight,
        arrival_date=arrival_date
    )

    session.add(package)
    session.commit()
    session.close()

    return "Package added successfully"




# E2 - Get Specific Package
def get_package(package_id):
    session = Session(engine)

    package = session.get(Packages, package_id)
    session.close()

    if package is None:
        return "not_found"

    return package


# E3 - Update Package
def update_package(package_id, package_name, destination, weight, arrival_date):
    session = Session(engine)

    package = session.get(Packages, package_id)

    if package is None:
        session.close()
        return "not_found"

    if package_name is not None:
        package.package_name = package_name

    if destination is not None:
        package.destination = destination

    if weight is not None:
        package.weight = weight

    if arrival_date is not None:
        package.arrival_date = arrival_date

    session.commit()
    session.close()

    return "Package updated successfully"


# E4 - Delete Package
def delete_package(package_id):
    session = Session(engine)

    package = session.get(Packages, package_id)

    if package is None:
        session.close()
        return "not_found"

    if package.status == "dispatched":
        session.close()
        return "dispatched"

    session.delete(package)
    session.commit()
    session.close()

    return "Package deleted successfully"


# E5 - Filter Packages
def filter_packages(destination, status):
    session = Session(engine)

    query = session.query(Packages)

    if destination is not None:
        query = query.filter(Packages.destination == destination)

    if status is not None:
        query = query.filter(Packages.status == status)

    packages = query.all()
    session.close()

    return packages




























def verify_login(username, password):
    if username ==USERNAME and password == PASSWORD:
        token = create_token(username=username)
        return token
    return False

def create_token(username):
    payload ={
        "username": username,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRY)
    }
    token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except:
        return False

    