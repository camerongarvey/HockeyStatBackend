from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import updater

app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder where CSVs are stored
DATA_DIR = "output_data"

@app.get("/team-data")
async def get_team_data(team: str = Query(..., description="Team name")):
    file_path = os.path.join(DATA_DIR, f"{team}.csv")
    print(team)
    if not os.path.exists(file_path):
        return {"error": f"No data found for team '{team}'"}

    df = pd.read_csv(file_path)

    return df.to_dict(orient="records")

@app.get("/all-teams")
async def find_all_teams():
    files = [os.path.splitext(f)[0] for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]

    return files

@app.get("/refresh")
def refresh(team: str = Query(..., description="Team name"), password: str = Query(..., description="Password")):
    if password == "cameron":
        print("Starting update")
        print(team)
        updater.update_data(team)
        return {"success": True}

@app.get("/ping")
def ping():
    print("pong")
    return {"ping": "pong"}


