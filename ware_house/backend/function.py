from sqlalchemy import Integer, String, Column, create_engine, Float, Date, ForeignKey
from sqlalchemy.orm import Session, declarative_base
from datetime import date, datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher()
DB_PATH = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base = declarative_base()


WAREHOUSE_MODULES = ["Packages", "Dispatch", "Analytics"]


USERNAME = "Poojitha"
PASSWORD = "123"


ACCESS_TOKEN_EXPIRY = 30 #mins
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



class User(Base):
    __tablename__ = "Users"
    user_id = Column[int](Integer, primary_key=True)
    username = Column[str](String)
    password = Column[str](String)
    user_type = Column(String, default="staff")
    

      


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
        arrival_date=arrival_date,
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


# E6
def get_dispatch(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)
    batches = session.query(DispatchBatches)
    if destination:
        batches = batches.filter(DispatchBatches.destination == destination)
    if vehicle:
        batches = batches.filter(DispatchBatches.vehicle == vehicle)
    if dispatch_status:
        batches = batches.filter(DispatchBatches.dispatch_status == dispatch_status)
    response = []
    for batch in batches.all():
        packages = session.query(Packages).filter(
            Packages.dispatch_batch_id == batch.id).all()
        response.append({
            "id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "dispatch_status": batch.dispatch_status,
            "dispatch_date": str(batch.dispatch_date) if batch.dispatch_date else None,
            "package_ids": [p.id for p in packages]
        })
    session.close()
    return response


# E7
def get_warehouse_statistics():
    session = Session(engine)
    total = session.query(Packages).count()
    dispatched = session.query(Packages).filter(Packages.status == "dispatched").count()
    packages = session.query(Packages).all()
    destinations = {}
    for package in packages:
        name = package.destination
        if name not in destinations:
            destinations[name] = 0
        destinations[name] += 1
    response = {
        "total_packages": total,
        "pending_packages": total - dispatched,
        "dispatched_packages": dispatched,
        "destination_wise_count": destinations
    }
    session.close()
    return response


# E8 - Create Dispatch Batch
def add_dispatch(destination, vehicle, package_ids):
    session = Session(engine)

    # check every package before writing anything, so a bad id leaves no empty batch
    packages = []
    for package_id in package_ids:
        package = session.get(Packages, package_id)

        if package is None:
            session.close()
            return "not_found"

        if package.status == "dispatched":
            session.close()
            return "already_dispatched"

        if package.destination != destination:
            session.close()
            return "invalid_destination"

        packages.append(package)

    dispatch = DispatchBatches(
        destination=destination,
        vehicle=vehicle,
        dispatch_status="dispatched"
    )
    session.add(dispatch)
    session.flush()  # gives dispatch.id before the single commit

    for package in packages:
        package.status = "dispatched"
        package.dispatch_batch_id = dispatch.id

    session.commit()
    session.close()

    return "Dispatch batch created successfully"


def filter_packages(destination=None, status=None):
    session = Session(engine)

    query = session.query(Packages)

    if destination:
        query = query.filter(Packages.destination == destination)

    if status:
        query = query.filter(Packages.status == status)

    packages = query.all()

    session.close()

    return packages






def verify_login(username, password):
    session = Session(engine)
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        session.close()
        return False
    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        session.close()
        return False
    user_type = user.user_type
    session.close()
    # instead of return true
    access_token = create_token(username=username, token_type="access", user_type=user_type)
    refresh_token = create_token(username=username, token_type="refresh", user_type=user_type)
    return {"access_token": access_token, "refresh_token": refresh_token}



        
def create_token(username, token_type, user_type="staff"):
    time = ACCESS_TOKEN_EXPIRY
    if token_type == "refresh":
        time = REFRESH_TOKEN_EXPIRY
    payload ={
        "username": username,
        "token_type": token_type,
        "user_type": user_type,
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




def get_user_role(token):

    try:
        payload = jwt.decode(
            jwt=token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload["token_type"] != "access":
            return False

        return payload["user_type"]

    except:
        return False



    

# --------Users-------------
def register_User(username:str, password:str, user_type: str = "staff"):
    session = Session(engine)
    user_exists = session.query(User).filter_by(username=username).first()
    if user_exists:
        session.close()
        return False
    session.add(User(username=username, password=ph.hash(password), user_type=user_type))
    session.commit()
    session.close()
    return True
