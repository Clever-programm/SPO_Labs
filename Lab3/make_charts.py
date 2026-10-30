import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "measurements"
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

for candidate in ["Times New Roman", "Liberation Serif", "DejaVu Serif"]:
    try:
        font_manager.findfont(candidate, fallback_to_default=False)
        plt.rcParams["font.family"] = candidate
        break
    except ValueError:
        pass
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11

COLORS = {"all": "#2F5597", "one": "#C55A11", "active": "#548235", "inactive": "#7F6000"}
LABELS = ["Ниже\nнормального", "Нормальный", "Выше\nнормального"]
X = [0, 1, 2]


def finish(fig, name):
    fig.tight_layout()
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def series(data, group, one_core, field):
    subset = [r for r in data if r["group"] == group and r["one_core"] == one_core]
    subset.sort(key=lambda r: r["priority"])
    return [r[field] for r in subset]


data = json.loads((OUT / "results_p2_p4.json").read_text(encoding="utf-8"))

fig, ax = plt.subplots(figsize=(8.2, 4.6))
for key, core, label in [("all", False, "Все ядра"), ("one", True, "Одно ядро")]:
    values = [v / 1e6 for v in series(data, "p2", core, "avg1")]
    ax.plot(X, values, marker="o", linewidth=2.2, color=COLORS[key], label=label)
    for x, y in zip(X, values):
        offset = -18 if key == "one" and y > 50 and x in (0, 1) else 8
        ax.annotate(f"{y:.2f}", (x, y), xytext=(0, offset), textcoords="offset points", ha="center")
ax.set_xticks(X, LABELS)
ax.set_ylabel("Итераций потока 1, млн/с")
ax.set_xlabel("Приоритет первого потока")
ax.set_title("Приоритет заметно влияет на производительность при одном ядре")
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
finish(fig, "graph_p2.png")

p3 = json.loads((OUT / "results_p3.json").read_text(encoding="utf-8"))
fig, ax = plt.subplots(figsize=(8.2, 4.6))
for key, field, label in [("active", "active_avg1", "Активное окно"),
                          ("inactive", "inactive_avg1", "Неактивное окно")]:
    values = [r[field] / 1e6 for r in p3]
    ax.plot(X, values, marker="o", linewidth=2.2, color=COLORS[key], label=label)
    for x, y in zip(X, values):
        offset = -18 if key == "one" and y > 50 and x in (0, 1) else 8
        ax.annotate(f"{y:.2f}", (x, y), xytext=(0, offset), textcoords="offset points", ha="center")
ax.set_xticks(X, LABELS)
ax.set_ylabel("Итераций потока 1, млн/с")
ax.set_xlabel("Приоритет первого потока")
ax.set_title("При параллельной работе двух копий влияние окна нестабильно")
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
finish(fig, "graph_p3.png")

fig, ax = plt.subplots(figsize=(8.2, 4.6))
for key, core, label in [("all", False, "Все ядра"), ("one", True, "Одно ядро")]:
    values = series(data, "p4", core, "avg1")
    ax.plot(X, values, marker="o", linewidth=2.2, color=COLORS[key], label=label)
    for x, y in zip(X, values):
        offset = -18 if key == "one" and y > 50 and x in (0, 1) else 8
        ax.annotate(f"{y:.2f}", (x, y), xytext=(0, offset), textcoords="offset points", ha="center")
ax.set_xticks(X, LABELS)
ax.set_ylabel("Итераций потока 1, 1/с")
ax.set_xlabel("Приоритет первого потока")
ax.set_title("Задержка 5 мс нивелирует влияние приоритета")
ax.set_ylim(63.5, 66.0)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
finish(fig, "graph_p4.png")

text = (OUT / "p5_one_starvation.txt").read_bytes().decode("cp1251", errors="replace")
rows5 = [tuple(map(int, m.groups())) for line in text.splitlines()
         if (m := re.fullmatch(r"(\d+);(\d+);(\d+)", line.strip()))]
seconds = [r[0] for r in rows5]
values1 = [r[1] / 1e6 for r in rows5]
values2 = [r[2] / 1e6 for r in rows5]
fig, ax = plt.subplots(figsize=(8.2, 4.6))
ax.plot(seconds, values2, marker="o", linewidth=2.0, color=COLORS["all"], label="Поток 2: HIGHEST")
ax.plot(seconds, values1, marker="o", linewidth=2.0, color=COLORS["one"], label="Поток 1: LOWEST")
for x, y in zip(seconds, values1):
    if y > 0:
        ax.annotate(f"{y:.2f}", (x, y), xytext=(0, 8), textcoords="offset points", ha="center")
ax.set_xlabel("Время, с")
ax.set_ylabel("Итераций, млн/с")
ax.set_title("Динамическое повышение приоритета периодически снимает голодание")
ax.set_xticks(seconds)
ax.grid(axis="y", alpha=0.25)
ax.legend(frameon=False)
finish(fig, "graph_p5.png")

print("Созданы графики:", ", ".join(p.name for p in ASSETS.glob("graph_*.png")))
