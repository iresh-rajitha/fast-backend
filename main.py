from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

UPLOAD_DIRECTORY = "./uploaded_files"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# print ip address when start up
import socket


def get_local_ip():
    try:
        # Use the local network's default gateway or another known address
        # Use a non-routable meta-address for local network, e.g., 192.168.1.1
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.1.1", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


print(get_local_ip())


# print current ip address for local network
def get_subnet_mask(interface='wlp0s20f3'):
    import fcntl
    import struct
    try:
        # Open a socket to retrieve subnet mask
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Fetch the subnet mask for the given interface
        subnet_mask = fcntl.ioctl(
            s.fileno(),
            0x891b,  # SIOCGIFNETMASK
            struct.pack('256s', interface.encode('utf-8'))
        )[20:24]
        subnet_mask = socket.inet_ntoa(subnet_mask)
        s.close()
        return subnet_mask
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


local_ip = get_local_ip()


# Enable CORS
origins = [
    "http://localhost:5173",  # React frontend running on port 5173
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Adjust as per your API methods
    allow_headers=["*"],
)

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")


@app.get("/ip")
async def get_ip():
    local_ip = get_local_ip()
    if local_ip:
        return {"ip": local_ip}
    return {"error": "Could not determine local IP address."}


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
