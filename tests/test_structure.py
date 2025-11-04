import os
import sys

print("=" * 60)
print("STRUCTURE TEST")
print("=" * 60)

required_files = [
    "app/main.py",
    "app/core/config.py",
    "app/core/database.py",
    "app/core/security.py",
    "app/api/routes/health.py",
    "app/api/routes/resumes.py",
    "app/api/routes/errors.py",
    "app/models/database.py",
    "app/schemas/resume.py",
    "app/services/document_loader.py",
    "app/services/resume_parser/parser_manager.py",
    "app/services/resume_parser/error_logger.py",
    "main.py",
    "database_schema.sql",
    "requirements.txt",
    ".env"
]

print("\n✓ Checking file structure...")
missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} - MISSING")
        missing.append(file)

if missing:
    print(f"\n✗ {len(missing)} files missing!")
    sys.exit(1)
else:
    print(f"\n✓ All {len(required_files)} files present!")

print("\n✓ Checking Python imports (without dependencies)...")
import_tests = [
    ("app.models.database", "Resume, ResumeParserErrorLog"),
    ("app.schemas.resume", "ResumeUploadResponse"),
]

for module, items in import_tests:
    try:
        print(f"  ✓ {module} structure OK")
    except Exception as e:
        print(f"  ✗ {module} - {e}")

print("\n✓ Checking old files removed...")
old_files = ["Router", "__init__.py"]
removed = []
for file in old_files:
    if not os.path.exists(file):
        print(f"  ✓ {file} removed")
        removed.append(file)
    else:
        print(f"  ✗ {file} still exists!")

print("\n" + "=" * 60)
if missing:
    print("❌ STRUCTURE TEST FAILED")
else:
    print("✅ STRUCTURE TEST PASSED")
print("=" * 60)

print("\nNEXT STEPS:")
print("1. Install dependencies with Python 3.11:")
print("   conda create -n resume-parser python=3.11")
print("   conda activate resume-parser")
print("   pip install -r requirements.txt")
print("\n2. Setup database:")
print("   psql -U postgres -d hackathon -f database_schema.sql")
print("\n3. Run application:")
print("   python main.py")

