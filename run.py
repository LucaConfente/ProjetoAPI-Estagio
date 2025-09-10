import uvicorn

if __name__ == "__main__":
    uvicorn.run("uweb_interface.backend.app:app", reload=True)
