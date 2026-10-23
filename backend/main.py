# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.
from fastapi import FastAPI

#Initialize FastAPI app and add health check endpoint for monitoring the backend service.
app = FastAPI()
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


