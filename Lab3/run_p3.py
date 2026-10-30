import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXE = ROOT / "x64" / "Release" / "SPO_Lr3.exe"
OUT = ROOT / "measurements"


def start(priority, name, copy, duration):
    path = OUT / f"p3_{name}_{copy}.txt"
    raw = path.open("wb")
    proc = subprocess.Popen(
        [str(EXE), str(priority), "0", "0", str(duration), f"SPO_Lr3_{name}_{copy}"],
        stdout=raw, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return proc, raw, path


def rows(path):
    text = path.read_bytes().decode("cp1251", errors="replace")
    return [tuple(map(int, m.groups())) for line in text.splitlines()
            if (m := re.fullmatch(r"(\d+);(\d+);(\d+)", line.strip()))]


def avg1(data, first, last):
    selected = [r[1] for r in data if first <= r[0] <= last]
    if len(selected) != last - first + 1:
        raise RuntimeError(f"Неполная серия {first}–{last}: {selected}")
    return sum(selected) / len(selected)


def main():
    results = []
    for priority, name in [(-1, "below"), (0, "normal"), (1, "above")]:
        # Новое консольное окно автоматически становится активным.
        # Фаза 1: A активна, B в фоне; фаза 2: B активна, A в фоне.
        b1, b1raw, b1path = start(priority, name, "B_inactive", 12)
        time.sleep(0.5)
        a, araw, apath = start(priority, name, "A", 24)
        b1.wait(timeout=20)
        b1raw.close()
        b2, b2raw, b2path = start(priority, name, "B_active", 12)
        a.wait(timeout=20)
        araw.close()
        b2.wait(timeout=20)
        b2raw.close()

        arows = rows(apath)
        active_a = avg1(arows, 2, 11)
        inactive_a = avg1(arows, 14, 23)
        active_b = avg1(rows(b2path), 2, 11)
        inactive_b = avg1(rows(b1path), 2, 11)
        result = {
            "priority": priority,
            "active_avg1": (active_a + active_b) / 2,
            "inactive_avg1": (inactive_a + inactive_b) / 2,
            "active_a": active_a, "active_b": active_b,
            "inactive_a": inactive_a, "inactive_b": inactive_b,
        }
        results.append(result)
        print(name, round(result["active_avg1"]), round(result["inactive_avg1"]), flush=True)
    (OUT / "results_p3.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
