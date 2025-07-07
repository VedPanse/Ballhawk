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
    allow_origins=["*"],  # Update to specific origin in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static image directory
if not os.path.exists("images"):
    os.mkdir("images")
app.mount("/images", StaticFiles(directory="images"), name="images")

@app.post("/predict")
async def predict(team1: str = Form(...), team2: str = Form(...), venue: str = Form(...)):
    if team1 == team2:
        return JSONResponse(status_code=400, content={"error": "Teams must be different"})

    print(f"[INFO] Generating prediction for: {team1} vs {team2} at {venue}")

    try:
        # Run main.py and capture its stdout (which returns image path)
        result = subprocess.run(
            ["python", "main.py", team1, team2, venue],
            check=True,
            capture_output=True,
            text=True
        )

        output_path = result.stdout.strip().splitlines()[-1]  # Last printed line = image path

        if not os.path.exists(output_path):
            return JSONResponse(status_code=500, content={"error": f"Expected output image not found at {output_path}"})

        # Copy image to public folder with UUID
        unique_filename = f"{uuid.uuid4().hex}.png"
        final_path = os.path.join("images", unique_filename)
        shutil.copy(output_path, final_path)

        print(f"[INFO] Copied heatmap to {final_path}")
        return FileResponse(final_path, media_type="image/png")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Script failed: {e.stderr}")
        return JSONResponse(status_code=500, content={"error": "Script execution failed", "details": e.stderr})
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Unexpected error", "details": str(e)})
