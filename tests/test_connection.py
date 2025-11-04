import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    print(f"✓ Configuration loaded successfully")
    print(f"  Database: {settings.DB_NAME}")
    print(f"  Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"  Max file size: {settings.MAX_FILE_SIZE_MB}MB")
    print(f"  OpenRouter Model: {settings.OPENAI_MODEL}")
except Exception as e:
    print(f"✗ Configuration error: {e}")
    sys.exit(1)

try:
    from app.core.database import engine
    with engine.connect() as connection:
        print(f"✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    sys.exit(1)

try:
    from app.models.database import Resume, ResumeParserErrorLog
    print(f"✓ Models imported successfully")
except Exception as e:
    print(f"✗ Model import error: {e}")
    sys.exit(1)

print("\n✓ All connection tests passed!")

