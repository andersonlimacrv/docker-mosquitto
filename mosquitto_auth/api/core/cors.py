from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
  origins = [
    "*",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://localhost:8002",
  ]
  app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )