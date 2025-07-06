from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import uuid
import os
import shutil

app = FastAPI()

# CORS: Allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: Serve static files (e.g. images) from /images
if not os.path.exists("images"):
    os.mkdir("images")
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.post("/predict")
async def predict(team1: str = Form(...), team2: str = Form(...), venue: str = Form(...)):
    if team1 == team2:
        return JSONResponse(status_code=400, content={"error": "Teams must be different"})

    print(f"[INFO] Generating prediction for: {team1} vs {team2} at {venue}")
    
    try:
        # Run main.py with args
        result = subprocess.run(
            ["python", "main.py", team1, team2, venue],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)

        output_path = "latest_output.png"
        if not os.path.exists(output_path):
            return JSONResponse(status_code=500, content={"error": "Output image not found"})

        # Copy image with a unique name
        unique_filename = f"{uuid.uuid4().hex}.png"
        final_path = os.path.join("images", unique_filename)
        shutil.copy(output_path, final_path)

        return FileResponse(final_path, media_type="image/png")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Script failed: {e.stderr}")
        return JSONResponse(status_code=500, content={"error": "Script failed", "details": e.stderr})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Unknown error", "details": str(e)})
