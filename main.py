from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
import updater
from pathlib import Path

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
DATA_DIR = "output_data/"


def count_files_in_folder(folder_path):
    path = Path(folder_path)
    num_files = len([p for p in path.iterdir() if p.is_file()])
    return num_files


@app.get("/team-data")
async def get_team_data(team: str = Query(..., description="Team name"),
                        schedule: str = Query(..., description="Schedule name")):
    file_path = DATA_DIR + schedule + f"/{team}.csv"
    if not os.path.exists(file_path):
        return {"error": f"No data found for team '{team}'"}

    df = pd.read_csv(file_path)

    return df.to_dict(orient="records")


@app.get("/games-played")
async def get_team_data(team: str = Query(..., description="Team name"),
                        schedule: str = Query(..., description="Schedule name")):
    file_path = "data/" + schedule + f"/{team}"
    games = count_files_in_folder(file_path)
    if not os.path.exists(file_path):
        return {"error": f"No data found for team '{team}'"}
    return games


@app.get("/all-teams")
async def find_all_teams():
    files = [os.path.splitext(f)[0] for f in os.listdir(DATA_DIR + "/complete") if
             os.path.isfile(os.path.join(DATA_DIR + "/complete", f))]

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
    return {"ping": "pong"}
