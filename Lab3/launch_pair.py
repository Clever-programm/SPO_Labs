import subprocess
import sys
from pathlib import Path

priority = int(sys.argv[1])
name = sys.argv[2]
root = Path(__file__).resolve().parent
exe = root / "x64" / "Release" / "SPO_Lr3.exe"
out = root / "measurements"
out.mkdir(exist_ok=True)
processes = []
for copy in ("A", "B"):
    raw = (out / f"p3_{name}_{copy}.txt").open("wb")
    proc = subprocess.Popen(
        [str(exe), str(priority), "0", "0", "180", f"SPO_Lr3_{name}_{copy}"],
        stdout=raw, stderr=subprocess.STDOUT,
        creationflags=subprocess.CREATE_NEW_CONSOLE)
    processes.append(proc.pid)
print(*processes)
