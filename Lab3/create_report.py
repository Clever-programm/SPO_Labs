import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Отчет_СПО_ЛР3.docx"
ASSETS = ROOT / "assets"
MEAS = ROOT / "measurements"
data = json.loads((MEAS / "results_p2_p4.json").read_text(encoding="utf-8"))
p3 = json.loads((MEAS / "results_p3.json").read_text(encoding="utf-8"))
p5 = json.loads((MEAS / "p5.json").read_text(encoding="utf-8"))
source = (ROOT / "SPO_Lr3" / "SPO_Lr3.cpp").read_text(encoding="utf-8")

doc = Document()
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.top_margin = Cm(2)
section.right_margin = Cm(1.5)
section.bottom_margin = Cm(2)
section.left_margin = Cm(3)
section.different_first_page_header_footer = True

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(14)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15
for name in ("Heading 1", "Heading 2"):
    style = styles[name]
    style.font.name = "Times New Roman"
    style.font.size = Pt(14)
    style.font.bold = True
    style.font.color.rgb = None
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.keep_with_next = True


def format_run(run, size=14, bold=False, font="Times New Roman"):
    run.font.name = font
    run.font.size = Pt(size)
    run.bold = bold
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    return run


def add_para(text="", *, bold=False, size=14, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
             first=True, before=0, after=6, keep=False):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.keep_with_next = keep
    if first:
        p.paragraph_format.first_line_indent = Cm(1.25)
    format_run(p.add_run(text), size=size, bold=bold)
    return p


def add_mixed(parts, *, first=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    if first:
        p.paragraph_format.first_line_indent = Cm(1.25)
    for text, bold in parts:
        format_run(p.add_run(text), bold=bold)
    return p


def add_heading(text):
    p = doc.add_paragraph(style="Heading 1")
    p.paragraph_format.keep_with_next = True
    format_run(p.add_run(text), bold=True)
    return p


def add_caption(text):
    return add_para(text, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=8, keep=True)


def shade(cell, fill="E7E6E6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def add_table(headers, rows, widths_cm):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, width in enumerate(widths_cm):
        table.columns[i].width = Cm(width)
    all_rows = [headers] + rows
    for r_idx, values in enumerate(all_rows):
        row = table.rows[0] if r_idx == 0 else table.add_row()
        if r_idx == 0:
            repeat_header(row)
        for i, value in enumerate(values):
            cell = row.cells[i]
            cell.width = Cm(widths_cm[i])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.text = ""
            lines = str(value).split("\n")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            for j, line in enumerate(lines):
                if j:
                    p.add_run().add_break()
                format_run(p.add_run(line), size=11, bold=r_idx == 0)
            if r_idx == 0:
                shade(cell)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_figure(filename, caption, width_cm=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ASSETS / filename), width=Cm(width_cm))
    add_caption(caption)


def get(group, core, priority):
    return next(r for r in data if r["group"] == group and r["one_core"] == core and r["priority"] == priority)


def fmt_int(value):
    return f"{round(value):,}".replace(",", " ")


def fmt_m(value):
    return f"{value / 1e6:.2f}".replace(".", ",")


def fmt2(value):
    return f"{value:.2f}".replace(".", ",")


def priority_name(p):
    return {-1: "Ниже нормального", 0: "Нормальный", 1: "Выше нормального"}[p]


def priority_const(p):
    return {-1: "BELOW_NORMAL", 0: "NORMAL", 1: "ABOVE_NORMAL"}[p]


# Титульный лист.
for line in [
    "МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ",
    "РОССИЙСКОЙ ФЕДЕРАЦИИ",
    "Федеральное государственное бюджетное образовательное учреждение",
    "высшего образования",
    "САМАРСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ",
]:
    add_para(line, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=0)
add_para("", first=False, after=4)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(ASSETS / "samgtu_logo.png"), width=Cm(3.12))
for line in ["Институт автоматики и информационных технологий", "Кафедра «Информатика и вычислительная техника»"]:
    add_para(line, size=12, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=0)
add_para("", first=False, after=18)
add_para("ОТЧЕТ", size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=6)
add_para("о выполнении лабораторной работы №3", size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=12)
add_para("по дисциплине «Системное программное обеспечение»", align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=6)
add_para("на тему «Процессы и потоки. Исследование диспетчеризации потоков»", align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=20)
cover = doc.add_table(rows=0, cols=3)
cover.alignment = WD_TABLE_ALIGNMENT.CENTER
cover.autofit = False
for values in [
    ("Преподаватель", "доцент", "К.В. Портнов"),
    ("", "ст. преподаватель", "С.А. Федосов"),
    ("Студенты", "3-ИАИТ-119", "П.М. Марченко"),
    ("", "3-ИАИТ-119", "И.Д. Царегородцев"),
]:
    row = cover.add_row()
    for i, value in enumerate(values):
        cell = row.cells[i]
        cell.width = Cm([4.0, 6.0, 6.0][i])
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i == 2 else WD_ALIGN_PARAGRAPH.CENTER
        format_run(p.add_run(value), size=12)
add_para("", first=False, after=18)
add_para("Самара 2026 г.", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, first=False, after=0)
doc.add_page_break()

add_mixed([("Цель работы: ", True), ("знакомство со средствами создания и управления процессами и потоками, исследование алгоритма диспетчеризации потоков операционной системы Windows.", False)])
add_heading("Задание.")
tasks = [
    "разработать приложение с главным и двумя дополнительными потоками; дополнительные потоки должны вычислять тригонометрическое выражение, а главный — ежесекундно выводить и сбрасывать счетчики итераций;",
    "исследовать зависимость числа итераций от приоритета первого потока при нормальном приоритете второго, используя все ядра и одно ядро; построить графики;",
    "запустить две копии приложения и исследовать влияние активности окна;",
    "добавить задержку 5 мс в цикл каждого потока и повторить измерения для всех ядер и одного ядра;",
    "установить приоритеты LOWEST и HIGHEST, ограничить процесс одним ядром и наблюдать динамическое повышение приоритета;",
    "получить число потоков приложения и оценить загрузку процессора.",
]
for i, task in enumerate(tasks, 1):
    p = add_para(f"{i}) {task}", first=False)
    p.paragraph_format.left_indent = Cm(1.25)
    p.paragraph_format.first_line_indent = Cm(-0.63)
add_para("Работа выполнена в Microsoft Visual Studio на языке C++ в соответствии с методическими указаниями. Создано решение Lab3 с консольным приложением SPO_Lr3. Использованы функции Win32 API CreateThread, GetCurrentThread, SetThreadPriority, Sleep и сопутствующие функции управления дескрипторами. Для каждого условия выполнялась 8-секундная серия; в таблицах приведены средние значения за секунды 2–8, чтобы исключить запуск процесса из усреднения.")

add_heading("1. Использованные функции Win32 API.")
add_caption("Таблица 1 – Функции Win32 API, использованные в работе")
add_table(["Функция", "Назначение"], [
    ["CreateThread", "Создает дополнительный поток внутри текущего процесса"],
    ["GetCurrentThread", "Возвращает дескриптор текущего потока"],
    ["SetThreadPriority", "Устанавливает относительный приоритет потока"],
    ["Sleep", "Приостанавливает поток на заданное число миллисекунд"],
    ["GetCurrentProcessId", "Возвращает идентификатор текущего процесса"],
    ["InterlockedIncrement", "Атомарно увеличивает счетчик итераций"],
    ["InterlockedExchange", "Атомарно считывает счетчик и сбрасывает его в ноль"],
    ["WaitForSingleObject", "Ожидает завершения дополнительного потока"],
    ["CloseHandle", "Закрывает дескриптор потока"],
    ["SetConsoleTitle", "Задает заголовок окна для различения двух копий"],
], [5.0, 11.0])

add_heading("2. Тестовое приложение.")
add_para("Приложение содержит три потока: главный и два вычислительных. Каждый вычислительный поток получает структуру ThreadData, устанавливает свой приоритет и в бесконечном цикле вычисляет y += sin(x) · cos(x), увеличивая x на каждой итерации. Если задана задержка, после итерации вызывается Sleep(delay). Главный поток раз в секунду выводит оба счетчика и сбрасывает их. Атомарные операции использованы только для исключения потери обновлений при одновременном доступе к счетчику.")
add_para("Аргументы командной строки: приоритет первого потока, приоритет второго потока, задержка в миллисекундах и длительность измерения в секундах. Значения приоритетов: −2 — LOWEST, −1 — BELOW_NORMAL, 0 — NORMAL, 1 — ABOVE_NORMAL, 2 — HIGHEST. Нулевая длительность означает непрерывную работу. Полный исходный код приведен в разделе 8.")

add_heading("3. Задание 2. Влияние приоритета и числа доступных ядер.")
add_para("Приоритет второго потока установлен NORMAL. Для первого потока последовательно использованы BELOW_NORMAL, NORMAL и ABOVE_NORMAL. Ограничение одним ядром реализовано маской соответствия процессора 1 — тем же параметром, который изменяется командой «Задать соответствие» Диспетчера задач.")
add_caption("Таблица 2 – Среднее число итераций за секунду без задержки")
rows2 = []
for priority in (-1, 0, 1):
    all_cores, one = get("p2", False, priority), get("p2", True, priority)
    rows2.append([f"{priority_name(priority)}\n{priority_const(priority)}", fmt_m(all_cores["avg1"]), fmt_m(all_cores["avg2"]), fmt_m(one["avg1"]), fmt_m(one["avg2"])])
add_table(["Приоритет потока 1", "Все ядра,\nпоток 1, млн/с", "Все ядра,\nпоток 2, млн/с", "Одно ядро,\nпоток 1, млн/с", "Одно ядро,\nпоток 2, млн/с"], rows2, [4.0, 3.0, 3.0, 3.0, 3.0])
add_figure("graph_p2.png", "Рисунок 1 – Зависимость производительности первого потока от его приоритета")
add_mixed([("Вывод по эксперименту: ", True), ("при доступности всех ядер зависимость не является монотонной (61,02; 60,80; 42,70 млн/с), поскольку потоки могут выполняться на разных ядрах, а фоновая нагрузка влияет на результат. На одном ядре влияние приоритета выражено: при BELOW_NORMAL первый поток почти не получает процессорное время (0,04 млн/с), при NORMAL оба потока получают близкие доли (58,13 и 61,18 млн/с), а при ABOVE_NORMAL первый поток достигает 101,34 млн/с, второй — только 16,58 млн/с.", False)])

add_heading("4. Задание 3. Влияние активности окна при работе двух копий.")
add_para("Одновременно запущены две копии приложения с одинаковыми приоритетами. Измерения разделены на две 10-секундные фазы: в первой активна копия A, во второй — копия B. В таблице усреднены результаты первого потока обеих копий для активного и неактивного состояния; приоритет второго потока оставался NORMAL.")
add_caption("Таблица 3 – Производительность первого потока двух копий приложения")
add_table(["Приоритет потока 1", "Активное окно,\nмлн/с", "Неактивное окно,\nмлн/с"],
          [[f"{priority_name(r['priority'])}\n{priority_const(r['priority'])}", fmt_m(r["active_avg1"]), fmt_m(r["inactive_avg1"])] for r in p3],
          [7.0, 4.5, 4.5])
add_figure("graph_p3.png", "Рисунок 2 – Влияние активности окна на производительность потока")
add_mixed([("Вывод по эксперименту: ", True), ("устойчивого преимущества активного окна не обнаружено. При BELOW_NORMAL и NORMAL активная копия выполнила меньше итераций (37,80 против 43,86 и 48,49 против 64,96 млн/с), а при ABOVE_NORMAL — больше (84,74 против 62,84 млн/с). Следовательно, при доступных 16 логических процессорах и изменчивой фоновой нагрузке активность окна не является основным фактором производительности; решающее значение имеют приоритет и распределение потоков планировщиком.", False)])

add_heading("5. Задание 4. Влияние задержки 5 мс.")
add_para("В цикл каждого вычислительного потока добавлена задержка Sleep(5). Остальные условия соответствуют заданию 2.")
add_caption("Таблица 4 – Среднее число итераций за секунду с задержкой 5 мс")
rows4 = []
for priority in (-1, 0, 1):
    all_cores, one = get("p4", False, priority), get("p4", True, priority)
    rows4.append([f"{priority_name(priority)}\n{priority_const(priority)}", fmt2(all_cores["avg1"]), fmt2(all_cores["avg2"]), fmt2(one["avg1"]), fmt2(one["avg2"])])
add_table(["Приоритет потока 1", "Все ядра,\nпоток 1, 1/с", "Все ядра,\nпоток 2, 1/с", "Одно ядро,\nпоток 1, 1/с", "Одно ядро,\nпоток 2, 1/с"], rows4, [4.0, 3.0, 3.0, 3.0, 3.0])
add_figure("graph_p4.png", "Рисунок 3 – Зависимость производительности от приоритета при задержке 5 мс")
add_mixed([("Вывод по эксперименту: ", True), ("число итераций практически не зависит от приоритета и числа ядер и составляет 64,57–65,14 1/с. Потоки большую часть времени находятся в состоянии ожидания, поэтому не конкурируют за процессор. Полученная частота соответствует фактическому периоду ожидания около 15,4 мс, а не номинальным 5 мс.", False)])

add_heading("6. Задание 5. Голодание и динамическое повышение приоритета.")
add_para("Первому потоку установлен приоритет THREAD_PRIORITY_LOWEST, второму — THREAD_PRIORITY_HIGHEST, процесс ограничен одним ядром. В таблице приведены все секундные измерения без усреднения. Первая секунда включает запуск и установку ограничения, поэтому не отражает установившийся режим.")
add_caption("Таблица 5 – Число итераций при приоритетах LOWEST и HIGHEST на одном ядре")
add_table(["Секунда", "Поток 1 (LOWEST), итераций", "Поток 2 (HIGHEST), итераций"],
          [[str(r[0]), fmt_int(r[1]), fmt_int(r[2])] for r in p5], [2.5, 6.75, 6.75])
add_figure("graph_p5.png", "Рисунок 4 – Голодание потока LOWEST и всплески его активности")
add_mixed([("Вывод по эксперименту: ", True), ("со 2-й по 15-ю секунду первый поток большую часть времени получает 0 итераций, поскольку процессор занят потоком HIGHEST. В 7-ю секунду выполнены 38 953 итерации, а в 12-ю — 2 278 719 итераций. Эти кратковременные всплески показывают, что Windows динамически повышает приоритет длительно ожидающего потока и предотвращает его постоянное голодание.", False)])

add_heading("7. Задание 6. Число потоков и загрузка процессора.")
add_para("Во время непрерывного запуска SPO_Lr3.exe с двумя потоками NORMAL получены сведения о процессе и сделан снимок Диспетчера задач. Число потоков подтверждено средствами Windows Get-Process, загрузка процесса оценена по приращению его процессорного времени за одну секунду.")
add_caption("Таблица 6 – Сведения о тестовом приложении")
add_table(["Показатель", "Значение"], [
    ["Идентификатор процесса", "22660"],
    ["Количество потоков", "3"],
    ["Логических процессоров в системе", "16"],
    ["Загрузка процессора процессом", "14,1 %"],
    ["Общая загрузка ЦП на снимке Диспетчера задач", "32 %"],
], [11.0, 5.0])
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.keep_with_next = True
p.add_run().add_picture(str(ROOT / "taskmanager.png"), width=Cm(15.5))
add_caption("Рисунок 5 – Диспетчер задач во время работы тестового приложения")
add_mixed([("Вывод по эксперименту: ", True), ("процесс имеет ожидаемые три потока — главный и два дополнительных. Два вычислительных потока занимают примерно два логических процессора: 2 / 16 · 100 % = 12,5 % общей производительности; измеренные 14,1 % близки к этой оценке с учетом колебаний частоты и фоновой активности.", False)])

add_heading("8. Исходный код тестового приложения.")
add_caption("Листинг 1 – Файл SPO_Lr3.cpp")
for line in source.splitlines():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    format_run(p.add_run(line or " "), size=9, font="Consolas")

add_para("", first=False, after=0)
add_mixed([("Вывод: ", True), ("в ходе работы разработано приложение с тремя потоками, использующее Win32 API для создания потоков, изменения их приоритетов и измерения числа вычислительных итераций. Эксперименты показали, что приоритет существенно влияет на производительность при конкуренции за один процессор: повышение приоритета первого потока увеличивает его долю процессорного времени и уменьшает долю второго. При доступности нескольких ядер эта зависимость слабее и может маскироваться параллельным выполнением и фоновой нагрузкой. Задержка в цикле устраняет конкуренцию за процессор, поэтому влияние приоритета почти исчезает. При крайних приоритетах наблюдается голодание низкоприоритетного потока, периодически прерываемое динамическим повышением его приоритета. Критерием влияния приоритета на производительность является устойчивое различие числа итераций при одинаковой вычислительной работе и неизменных прочих условиях; наиболее явно оно проявляется при ограничении одним ядром и отсутствии задержек.", False)])

# Номер страницы в нижнем колонтитуле; на титульном листе он скрыт.
footer_p = section.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = footer_p.add_run()
format_run(run, size=12)
begin = OxmlElement("w:fldChar")
begin.set(qn("w:fldCharType"), "begin")
instr = OxmlElement("w:instrText")
instr.set(qn("xml:space"), "preserve")
instr.text = " PAGE "
end = OxmlElement("w:fldChar")
end.set(qn("w:fldCharType"), "end")
run._r.extend([begin, instr, end])

doc.save(OUT)
print(OUT)
