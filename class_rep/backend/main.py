from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"])

functions.initialize_database()

REGISTER_TYPE = ["student", "candidate"]   # officer is not allowed to register
PHASES = ["nominations", "voting", "closed"]


def check_role(token, allowed_roles):
    roll_no = functions.verify_token(token=token, token_type="access")
    if not roll_no:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_type = functions.get_user_role(token=token, token_type="access")

    if not user_type:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user_type not in allowed_roles:
        raise HTTPException(status_code=403, detail="Permission denied")

    # the logged-in roll number, so nobody can vote or withdraw as someone else
    return roll_no


class UserIn(BaseModel):
    roll_no: str = Field(min_length=1)
    password: str = Field(min_length=1)
    user_type: str


class LoginIn(BaseModel):
    roll_no: str = Field(min_length=1)
    password: str = Field(min_length=1)


class NominationCreate(BaseModel):
    name: str = Field(min_length=1)
    position: str
    manifesto: str = Field(min_length=30)


class VoteCreate(BaseModel):
    candidate_id: int


class PhaseUpdate(BaseModel):
    phase: str


# E1
@app.get("/candidates")
def get_candidates(position: str = None, approved_only: bool = False, token = Header(None)):
    check_role(token, ["student", "candidate", "officer"])
    if position and position not in functions.POSITIONS:
        raise HTTPException(status_code=422,detail="Invalid position")
    return functions.get_all_candidates(position, approved_only)

# E2
@app.get("/candidates/{candidate_id}")
def candidate(candidate_id: int, token = Header(None)):
    check_role(token, ["student", "candidate", "officer"])
    result = functions.get_candidate(candidate_id)
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    return result

# E3
@app.post("/candidates")
def nominate(nomination: NominationCreate, token = Header(None)):
    roll_no = check_role(token, ["candidate"])
    if nomination.position not in functions.POSITIONS:
        raise HTTPException(status_code=422, detail="Invalid position")
    result = functions.add_candidate(roll_no, nomination.name, nomination.position, nomination.manifesto)
    if result == "duplicate_roll":
        raise HTTPException(status_code=400, detail="This roll number already has an active nomination")
    return {"message": "Candidate nominated successfully"}

# E4
@app.patch("/candidates/{candidate_id}/approve")
def approve_candidate(candidate_id: int, token = Header(None)):
    check_role(token, ["officer"])
    response = functions.approve_candidate(candidate_id)
    if response == "phase_closed":
        raise HTTPException(status_code=400, detail="Nominations are closed")
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if response == "not_nominated":
        raise HTTPException(status_code=400, detail="Only nominated candidates can be approved")
    return {"message": "Candidate approved successfully"}

# E5
@app.patch("/candidates/{candidate_id}/withdraw")
def withdraw_candidate(candidate_id: int, token = Header(None)):
    roll_no = check_role(token, ["candidate"])
    response = functions.withdraw_candidate(candidate_id, roll_no)
    if response == "phase_closed":
        raise HTTPException(status_code=400, detail="Nominations are closed")
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Candidate not found")
    if response == "roll_mismatch":
        raise HTTPException(status_code=403, detail="You can only withdraw your own nomination")
    if response == "already_withdrawn":
        raise HTTPException(status_code=400, detail="Candidate is already withdrawn")
    return {"message": "Nomination withdrawn successfully"}

# E6
@app.get("/election/phase")
def get_election_phase(token = Header(None)):
    check_role(token, ["student", "candidate", "officer"])
    response = functions.get_election_phase()
    if response == "no_election":
        raise HTTPException(status_code=404, detail="Election not found")
    return {"phase": response}

# E7
@app.patch("/election/phase")
def change_phase(update: PhaseUpdate, token = Header(None)):
    check_role(token, ["officer"])
    if update.phase not in PHASES:
        raise HTTPException(status_code=422, detail="phase must be nominations, voting or closed")
    result = functions.change_phase(update.phase)
    if result == "no_election":
        raise HTTPException(status_code=404, detail="Election not found")
    if result == "no_candidate":
        raise HTTPException(status_code=400, detail="Every position must have at least one approved candidate")
    return result

# E8
@app.post("/votes")
def vote(ballot: VoteCreate, token = Header(None)):
    roll_no = check_role(token, ["student", "candidate"])
    result = functions.cast_vote(roll_no, ballot.candidate_id)
    if result == "voting_closed":
        raise HTTPException(status_code=400,detail="Voting is not open")
    if result == "not_found":
        raise HTTPException(status_code=404,detail="Candidate not found")
    if result == "not_approved":
        raise HTTPException(status_code=400,detail="Candidate not approved")
    if result == "already_voted":
        raise HTTPException(status_code=400,detail="Already voted for this position")

    return result

# E9
@app.get("/votes/{voter_roll}/positions")
def voted_positions(voter_roll: str, token = Header(None)):
    roll_no = check_role(token, ["student", "candidate", "officer"])
    user_type = functions.get_user_role(token=token, token_type="access")
    if user_type != "officer" and roll_no != voter_roll:
        raise HTTPException(status_code=403, detail="You can only see your own votes")
    return functions.get_voted_positions(voter_roll)

# E10
@app.get("/results")
def get_final_results(token = Header(None)):
    check_role(token, ["student", "candidate", "officer"])
    result = functions.get_results()
    if result == "not_closed":
        raise HTTPException(status_code=403, detail="Election is not closed")
    return result


#tokens
@app.post("/register")
def register_user(user: UserIn):
    if user.user_type not in REGISTER_TYPE:
        raise HTTPException(status_code=400, detail="user_type must be student or candidate")
    if functions.register_user(roll_no=user.roll_no, password=user.password, user_type=user.user_type):
        return {"message": "User registered successfully"}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/login")
def login(user: LoginIn):
    token = functions.verify_login(roll_no=user.roll_no, password=user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return token

@app.post("/refresh")
def refresh_token(refresh_token = Header(None)):
    roll_no = functions.verify_token(token=refresh_token, token_type="refresh")
    if not roll_no:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    # keep the same user_type, so an officer stays an officer after refresh
    user_type = functions.get_user_role(token=refresh_token, token_type="refresh")
    access_token = functions.create_token(roll_no=roll_no, token_type="access", user_type=user_type)
    return {"access_token": access_token}
