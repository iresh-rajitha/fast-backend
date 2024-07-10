from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

UPLOAD_DIRECTORY = "./uploaded_files"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Enable CORS
origins = [
    "http://localhost:5173",       # React frontend running on port 5173
    "http://192.168.8.132:3000",    # React frontend running on your specific IP address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Adjust as per your API methods
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), folder: str = ""):
    folder_path = os.path.join(UPLOAD_DIRECTORY, folder) if folder else UPLOAD_DIRECTORY
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_location = os.path.join(folder_path, file.filename)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/files")
async def list_files(folder: str = ""):
    folder_path = os.path.join(UPLOAD_DIRECTORY, folder) if folder else UPLOAD_DIRECTORY
    if not os.path.exists(folder_path):
        return JSONResponse(status_code=404, content={"error": "Folder not found"})
    files = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isdir(file_path):
            files.append({"name": file_name, "type": "folder"})
        else:
            files.append({"name": file_name, "type": "file"})
    return files

@app.get("/download")
async def download_file(folder: str = "", filename: str = ""):
    folder_path = os.path.join(UPLOAD_DIRECTORY, folder) if folder else UPLOAD_DIRECTORY
    file_path = os.path.join(folder_path, filename)
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
