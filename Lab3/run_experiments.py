import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXE = ROOT / "x64" / "Release" / "SPO_Lr3.exe"
OUT = ROOT / "measurements"
OUT.mkdir(exist_ok=True)
PRIORITIES = [(-1, "below"), (0, "normal"), (1, "above")]


def parse_output(text):
    rows = []
    for line in text.splitlines():
        m = re.fullmatch(r"(\d+);(\d+);(\d+)", line.strip())
        if m:
            rows.append(tuple(map(int, m.groups())))
    if not rows:
        raise RuntimeError("Нет числовых измерений: " + text)
    # Первую секунду отбрасываем: запуск и установка приоритетов.
    used = rows[1:] if len(rows) > 1 else rows
    return {
        "rows": rows,
        "avg1": sum(r[1] for r in used) / len(used),
        "avg2": sum(r[2] for r in used) / len(used),
    }


def run_one(group, priority, name, delay, one_core):
    label = f"{group}_{'one' if one_core else 'all'}_{name}"
    raw_path = OUT / (label + ".txt")
    args = [str(EXE), str(priority), "0", str(delay), "8"]
    with raw_path.open("wb") as raw:
        if one_core:
            proc = subprocess.Popen(args, stdout=raw, stderr=subprocess.STDOUT)
            # Маска 1 оставляет процессу только логический процессор 0 —
            # та же настройка, что «Задать соответствие» в Диспетчере задач.
            subprocess.run([
                "powershell", "-NoProfile", "-Command",
                f"(Get-Process -Id {proc.pid}).ProcessorAffinity = 1"
            ], check=True, capture_output=True, timeout=15)
            proc.wait(timeout=20)
        else:
            proc = subprocess.run(args, stdout=raw, stderr=subprocess.STDOUT, timeout=20)
    text = raw_path.read_bytes().decode("cp1251", errors="replace")
    result = parse_output(text)
    result.update({"group": group, "priority": priority, "delay": delay,
                   "one_core": one_core, "file": raw_path.name})
    print(label, round(result["avg1"]), round(result["avg2"]), flush=True)
    return result


def main():
    results = []
    for one_core in (False, True):
        for priority, name in PRIORITIES:
            results.append(run_one("p2", priority, name, 0, one_core))
            time.sleep(1)
    for one_core in (False, True):
        for priority, name in PRIORITIES:
            results.append(run_one("p4", priority, name, 5, one_core))
            time.sleep(1)
    (OUT / "results_p2_p4.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
