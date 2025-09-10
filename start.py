import subprocess
subprocess.Popen(fr'start cmd /K ".\PDVenv\Scripts\python.exe -m uvicorn backend.app.main:app --reload" ', shell=True)
subprocess.Popen(fr'start cmd /K ".\PDVenv\Scripts\python.exe frontend\main.py" ', shell=True)

