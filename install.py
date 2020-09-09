import os
import subprocess


src_folder = "src"
for folder in os.listdir(f"{src_folder}"):
    if "setup.py" in os.listdir(f"{src_folder}/{folder}"):
        print(f"Installing {folder}...")
        subprocess.run(["pip", "install", f"{src_folder}/{folder}"])
        print()

print(f"Installing other project dependencies...")
subprocess.run(["pip", "install", "."])
print()

print(f"Creating database...")
subprocess.run(["python", "manage.py", "migrate"])
print()