import os
import shutil

base_dir = r"e:\Kamalesh Project\SPORTFLASH"

dirs = [
    os.path.join(base_dir, "legacy", "AI"),
    os.path.join(base_dir, "core"),
    os.path.join(base_dir, "analytics"),
    os.path.join(base_dir, "pipeline"),
    os.path.join(base_dir, "tools"),
    os.path.join(base_dir, "api"),
    os.path.join(base_dir, "tests"),
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    init_file = os.path.join(d, "__init__.py")
    if not os.path.exists(init_file) and not d.endswith("legacy"):
        with open(init_file, "w") as f:
            f.write("# Module package initialization\n")

# Copy AI files to legacy/AI
ai_dir = os.path.join(base_dir, "AI")
legacy_ai_dir = os.path.join(base_dir, "legacy", "AI")

if os.path.exists(ai_dir):
    for item in os.listdir(ai_dir):
        src = os.path.join(ai_dir, item)
        dst = os.path.join(legacy_ai_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src) and item != "__pycache__":
            shutil.copytree(src, dst, dirs_exist_ok=True)

# Copy dashboard.py and dashboard_backup.py to legacy
for db_file in ["dashboard.py", "dashboard_backup.py"]:
    src = os.path.join(base_dir, db_file)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(base_dir, "legacy", db_file))

print("[INFO] Directory structure and legacy migration complete.")
