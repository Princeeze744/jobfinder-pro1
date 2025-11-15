import os
from pathlib import Path

# Current directory
base_path = Path.cwd()

# Define all files to create (relative to base path)
files = [
    ".env",
    ".gitignore",
    "requirements.txt",
    "setup.py",
    "run.sh",
    "src/__init__.py",
    "src/main.py",
    "src/config.py",
    "src/logger.py",
    "src/exceptions.py",
    "src/modules/__init__.py",
    "src/modules/cv_analyzer.py",
    "src/modules/company_finder.py",
    "src/modules/email_generator.py",
    "src/modules/email_sender.py",
    "src/modules/data_processor.py",
    "src/utils/__init__.py",
    "src/utils/validators.py",
    "src/utils/formatters.py",
    "src/utils/file_handler.py",
    "src/utils/api_client.py",
    "src/templates/email_template.html",
    "src/templates/email_template.txt",
    "src/data/sample_cv.txt",
    "src/data/companies_output.json",
    "src/data/emails_output.json",
    "tests/__init__.py",
    "tests/test_cv_analyzer.py",
    "tests/test_company_finder.py",
    "tests/test_email_generator.py",
    "tests/test_data_processor.py",
    "docs/README.md",
    "docs/SETUP.md",
    "docs/API_GUIDE.md",
    "docs/ARCHITECTURE.md"
]

# Create files
print("Creating all files...")
for file_path in files:
    full_path = base_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch(exist_ok=True)
    print(f"✓ Created: {file_path}")

print("\n" + "="*60)
print("✅ ALL FILES CREATED SUCCESSFULLY!")
print("="*60)
print(f"\nTotal files created: {len(files)}")
print(f"Location: {base_path}")