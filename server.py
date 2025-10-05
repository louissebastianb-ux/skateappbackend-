from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil
import cv2

app = FastAPI()

# 📁 Opprett mappe for video-data
DATASET_DIR = Path("dataset")
DATASET_DIR.mkdir(exist_ok=True)

# 📍 Eksempel skate spots (du kan utvide disse)
SPOTS = [
    {"name": "Rådhusplassen Rail", "lat": 59.9111, "lng": 10.7528, "trick": None},
    {"name": "Majorstua Banks", "lat": 59.9291, "lng": 10.7146, "trick": None},
    {"name": "Oslo S Ledges", "lat": 59.9106, "lng": 10.7579, "trick": None},
    {"name": "Lillehammer Stairs", "lat": 61.1153, "lng": 10.4662, "trick": None},
    {"name": "Trondheim Plaza Ledge", "lat": 63.4305, "lng": 10.3951, "trick": None},
]

@app.get("/spots")
def get_spots():
    """Returnerer alle skate spots."""
    return SPOTS


# 🧠 Midlertidig AI-funksjon (dummy)
def analyze_trick(video_path: str, trick: str):
    """
    Denne versjonen bruker ikke MediaPipe.
    Bare returnerer True slik at appen fungerer på Render.
    """
    print(f"Analyserer video: {video_path} for trikk: {trick}")
    return True


@app.post("/upload")
async def upload_video(category: str = Form(...), trick: str = Form(...), file: UploadFile = None):
    """
    Lagrer video og 'analyserer' trikket (dummy for nå).
    """
    try:
        save_dir = DATASET_DIR / category / trick
        save_dir.mkdir(parents=True, exist_ok=True)

        file_path = save_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        detected = analyze_trick(str(file_path), trick)

        return {
            "message": f"Video lastet opp til {category}/{trick}",
            "trick_detected": detected,
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/my_uploads")
def my_uploads():
    """
    Returnerer alle opplastede videoer sortert etter kategori og trikk.
    """
    uploads = {}
    for category in DATASET_DIR.iterdir():
        if category.is_dir():
            uploads[category.name] = {}
            for trick in category.iterdir():
                if trick.is_dir():
                    files = [
                        f"/videos/{category.name}/{trick.name}/{file.name}"
                        for file in trick.iterdir()
                        if file.is_file()
                    ]
                    uploads[category.name][trick.name] = files
    return uploads


# 🎥 Statisk server for videofiler
app.mount("/videos", StaticFiles(directory=DATASET_DIR), name="videos")
