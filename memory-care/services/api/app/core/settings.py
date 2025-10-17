import os
class Settings:
    def __init__(self):
        cors = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
        self.APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
        self.APP_PORT = int(os.getenv('APP_PORT', '8000'))
        self.CORS_ORIGINS = [o.strip() for o in cors if o.strip()]
settings = Settings()
