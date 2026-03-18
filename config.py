import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Rate limiting
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Valid sectors
VALID_SECTORS = [
    "pharmaceuticals", "technology", "agriculture", "automotive",
    "textiles", "chemicals", "electronics", "steel", "gems",
    "jewelry", "food", "beverages", "energy", "infrastructure",
    "finance", "healthcare", "education", "retail", "logistics",
    "manufacturing", "defence", "aerospace", "mining", "telecom",
]
