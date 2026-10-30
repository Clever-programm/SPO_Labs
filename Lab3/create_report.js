import fs from "node:fs";
import path from "node:path";
import {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, ImageRun,
  PageBreak, PageNumber, Packer, Paragraph, ShadingType, Table, TableCell,
  TableRow, TextRun, WidthType,
} from "docx";

const outputPath = process.argv[2];
if (!outputPath) throw new Error("Usage: node create_report.js /absolute/path/output.docx");
const root = path.dirname(outputPath);
const assets = path.join(root, "assets");
const measurements = path.join(root, "measurements");
const data = JSON.parse(fs.readFileSync(path.join(measurements, "results_p2_p4.json"), "utf8"));
const p3 = JSON.parse(fs.readFileSync(path.join(measurements, "results_p3.json"), "utf8"));
const p5 = JSON.parse(fs.readFileSync(path.join(measurements, "p5.json"), "utf8"));
const source = fs.readFileSync(path.join(root, "SPO_Lr3", "SPO_Lr3.cpp"), "utf8").replaceAll("\r", "");

const font = { ascii: "Times New Roman", hAnsi: "Times New Roman", cs: "Times New Roman", eastAsia: "Times New Roman" };
const codeFont = { ascii: "Consolas", hAnsi: "Consolas", cs: "Consolas", eastAsia: "Consolas" };
const run = (text, options = {}) => new TextRun({ text: String(text), font, size: 28, ...options });
const para = (children, options = {}) => new Paragraph({
  spacing: { after: 120, line: 276 },
  ...options,
  children: Array.isArray(children) ? children : [children],
});
const body = (text, options = {}) => para(run(text), {
  alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 }, ...options,
});
const heading = (text) => para(run(text, { bold: true }), {
  heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120, line: 276 }, keepNext: true,
});
const caption = (text) => para(run(text, { size: 24 }), {
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 240, line: 240 }, keepNext: true,
});
const empty = (after = 0) => para(run(""), { spacing: { after, line: 240 } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const fmtInt = (n) => Math.round(n).toLocaleString("ru-RU");
const fmtM = (n) => (n / 1e6).toFixed(2).replace(".", ",");
const fmt2 = (n) => n.toFixed(2).replace(".", ",");
const priorityName = (p) => p === -1 ? "Ниже нормального" : p === 0 ? "Нормальный" : "Выше нормального";
const priorityConst = (p) => p === -1 ? "BELOW_NORMAL" : p === 0 ? "NORMAL" : "ABOVE_NORMAL";

function cell(text, width, options = {}) {
  const { header = false, align = AlignmentType.CENTER, ...cellOptions } = options;
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    margins: { top: 70, bottom: 70, left: 90, right: 90 },
    verticalAlign: "center",
    ...cellOptions,
    children: String(text).split("\n").map(line => para(run(line, { size: 22, bold: header }), {
      alignment: align,
      spacing: { after: 0, line: 240 },
    })),
  });
}

function makeTable(headers, rows, widths) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      left: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      right: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
      insideVertical: { style: BorderStyle.SINGLE, size: 4, color: "000000" },
    },
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], {
        header: true, shading: { type: ShadingType.CLEAR, fill: "E7E6E6" },
      })) }),
      ...rows.map(row => new TableRow({ children: row.map((v, i) => cell(v, widths[i], {
        align: i === 0 && String(v).length > 24 ? AlignmentType.LEFT : AlignmentType.CENTER,
      })) })),
    ],
  });
}

function figure(file, width, naturalWidth, naturalHeight, title) {
  return [
    para(new ImageRun({ type: "png", data: fs.readFileSync(path.join(assets, file)),
      transformation: { width, height: Math.round(width * naturalHeight / naturalWidth) } }), {
      alignment: AlignmentType.CENTER, spacing: { before: 120, after: 0, line: 240 }, keepNext: true,
    }),
    caption(title),
  ];
}

function get(group, core, priority) {
  return data.find(r => r.group === group && r.one_core === core && r.priority === priority);
}

const children = [];
// Титульный лист по образцу предыдущих лабораторных работ.
children.push(para(run("МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ\nРОССИЙСКОЙ ФЕДЕРАЦИИ", { size: 24 }), { alignment: AlignmentType.CENTER }));
// Переносы на титульном листе оформляем отдельными абзацами.
children.pop();
for (const line of ["МИНИСТЕРСТВО ОБРАЗОВАНИЯ И НАУКИ", "РОССИЙСКОЙ ФЕДЕРАЦИИ",
  "Федеральное государственное бюджетное образовательное учреждение", "высшего образования",
  "САМАРСКИЙ ГОСУДАРСТВЕННЫЙ ТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ"]) {
  children.push(para(run(line, { size: 24 }), { alignment: AlignmentType.CENTER, spacing: { after: 0, line: 240 } }));
}
children.push(empty(80));
children.push(para(new ImageRun({ type: "png", data: fs.readFileSync(path.join(assets, "samgtu_logo.png")),
  transformation: { width: 90, height: 86 } }), { alignment: AlignmentType.CENTER, spacing: { after: 120 } }));
for (const line of ["Институт автоматики и информационных технологий", "Кафедра «Информатика и вычислительная техника»"]) {
  children.push(para(run(line, { size: 24 }), { alignment: AlignmentType.CENTER, spacing: { after: 0, line: 240 } }));
}
children.push(empty(300));
children.push(para(run("ОТЧЕТ", { bold: true, size: 30 }), { alignment: AlignmentType.CENTER, spacing: { after: 120 } }));
children.push(para(run("о выполнении лабораторной работы №3", { bold: true, size: 30 }), { alignment: AlignmentType.CENTER, spacing: { after: 240 } }));
children.push(para([run("по дисциплине  ", { size: 28 }), run("Системное программное обеспечение", { size: 28, underline: {} })], { alignment: AlignmentType.CENTER }));
children.push(para(run("на тему «Процессы и потоки. Исследование диспетчеризации потоков»", { size: 28 }), {
  alignment: AlignmentType.CENTER, spacing: { after: 360 },
}));
const coverRows = [
  ["Преподаватель", "доцент", "К.В. Портнов"],
  ["", "ст. преподаватель", "С.А. Федосов"],
  ["Студенты", "3-ИАИТ-119", "П.М. Марченко"],
  ["", "3-ИАИТ-119", "И.Д. Царегородцев"],
];
children.push(new Table({
  width: { size: 9000, type: WidthType.DXA }, columnWidths: [2200, 3300, 3500],
  rows: coverRows.map(row => new TableRow({ children: row.map((v, i) => cell(v, [2200, 3300, 3500][i], { align: i === 2 ? AlignmentType.RIGHT : AlignmentType.CENTER })) })),
}));
children.push(empty(300));
children.push(para(run("Самара 2026 г.", { size: 24 }), { alignment: AlignmentType.CENTER }));
children.push(pageBreak());

children.push(para([run("Цель работы: ", { bold: true }), run("знакомство со средствами создания и управления процессами и потоками, исследование алгоритма диспетчеризации потоков операционной системы Windows.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));
children.push(heading("Задание."));
const tasks = [
  "разработать приложение с главным и двумя дополнительными потоками; дополнительные потоки должны вычислять тригонометрическое выражение, а главный — ежесекундно выводить и сбрасывать счетчики итераций;",
  "исследовать зависимость числа итераций от приоритета первого потока при нормальном приоритете второго, используя все ядра и одно ядро; построить графики;",
  "запустить две копии приложения и исследовать влияние активности окна;",
  "добавить задержку 5 мс в цикл каждого потока и повторить измерения для всех ядер и одного ядра;",
  "установить приоритеты LOWEST и HIGHEST, ограничить процесс одним ядром и наблюдать динамическое повышение приоритета;",
  "получить число потоков приложения и оценить загрузку процессора.",
];
tasks.forEach((t, i) => children.push(para(run(`${i + 1}) ${t}`), { alignment: AlignmentType.JUSTIFIED, indent: { left: 709, hanging: 354 } })));
children.push(body("Работа выполнена в Microsoft Visual Studio на языке C++ в соответствии с методическими указаниями. Создано решение Lab3 с консольным приложением SPO_Lr3. Использованы функции Win32 API CreateThread, GetCurrentThread, SetThreadPriority, Sleep и сопутствующие функции управления дескрипторами. Для каждого условия выполнялась 8-секундная серия; в таблицах приведены средние значения за секунды 2–8, чтобы исключить запуск процесса из усреднения."));

children.push(heading("1. Использованные функции Win32 API."));
children.push(caption("Таблица 1 – Функции Win32 API, использованные в работе"));
children.push(makeTable(["Функция", "Назначение"], [
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
], [3000, 6000]));

children.push(heading("2. Тестовое приложение."));
children.push(body("Приложение содержит три потока: главный и два вычислительных. Каждый вычислительный поток получает структуру ThreadData, устанавливает свой приоритет и в бесконечном цикле вычисляет y += sin(x) · cos(x), увеличивая x на каждой итерации. Если задана задержка, после итерации вызывается Sleep(delay). Главный поток раз в секунду выводит оба счетчика и сбрасывает их. Атомарные операции использованы только для исключения потери обновлений при одновременном доступе к счетчику."));
children.push(body("Аргументы командной строки: приоритет первого потока, приоритет второго потока, задержка в миллисекундах и длительность измерения в секундах. Значения приоритетов: −2 — LOWEST, −1 — BELOW_NORMAL, 0 — NORMAL, 1 — ABOVE_NORMAL, 2 — HIGHEST. Нулевая длительность означает непрерывную работу. Полный исходный код приведен в разделе 8."));

children.push(heading("3. Задание 2. Влияние приоритета и числа доступных ядер."));
children.push(body("Приоритет второго потока установлен NORMAL. Для первого потока последовательно использованы BELOW_NORMAL, NORMAL и ABOVE_NORMAL. Ограничение одним ядром реализовано маской соответствия процессора 1 — тем же параметром, который изменяется командой «Задать соответствие» Диспетчера задач."));
children.push(caption("Таблица 2 – Среднее число итераций за секунду без задержки"));
const rows2 = [-1, 0, 1].map(p => {
  const all = get("p2", false, p), one = get("p2", true, p);
  return [`${priorityName(p)}\n${priorityConst(p)}`, fmtM(all.avg1), fmtM(all.avg2), fmtM(one.avg1), fmtM(one.avg2)];
});
children.push(makeTable(["Приоритет потока 1", "Все ядра,\nпоток 1, млн/с", "Все ядра,\nпоток 2, млн/с", "Одно ядро,\nпоток 1, млн/с", "Одно ядро,\nпоток 2, млн/с"], rows2, [2200, 1700, 1700, 1700, 1700]));
children.push(...figure("graph_p2.png", 620, 1447, 808, "Рисунок 1 – Зависимость производительности первого потока от его приоритета"));
children.push(para([run("Вывод по эксперименту: ", { bold: true }), run("при доступности всех ядер зависимость не является монотонной (61,02; 60,80; 42,70 млн/с), поскольку потоки могут выполняться на разных ядрах, а фоновая нагрузка влияет на результат. На одном ядре влияние приоритета выражено: при BELOW_NORMAL первый поток почти не получает процессорное время (0,04 млн/с), при NORMAL оба потока получают близкие доли (58,13 и 61,18 млн/с), а при ABOVE_NORMAL первый поток достигает 101,34 млн/с, второй — только 16,58 млн/с.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

children.push(heading("4. Задание 3. Влияние активности окна при работе двух копий."));
children.push(body("Одновременно запущены две копии приложения с одинаковыми приоритетами. Измерения разделены на две 10-секундные фазы: в первой активна копия A, во второй — копия B. В таблице усреднены результаты первого потока обеих копий для активного и неактивного состояния; приоритет второго потока оставался NORMAL."));
children.push(caption("Таблица 3 – Производительность первого потока двух копий приложения"));
children.push(makeTable(["Приоритет потока 1", "Активное окно,\nмлн/с", "Неактивное окно,\nмлн/с"],
  p3.map(r => [`${priorityName(r.priority)}\n${priorityConst(r.priority)}`, fmtM(r.active_avg1), fmtM(r.inactive_avg1)]), [4000, 2500, 2500]));
children.push(...figure("graph_p3.png", 620, 1446, 807, "Рисунок 2 – Влияние активности окна на производительность потока"));
children.push(para([run("Вывод по эксперименту: ", { bold: true }), run("устойчивого преимущества активного окна не обнаружено. При BELOW_NORMAL и NORMAL активная копия выполнила меньше итераций (37,80 против 43,86 и 48,49 против 64,96 млн/с), а при ABOVE_NORMAL — больше (84,74 против 62,84 млн/с). Следовательно, при доступных 16 логических процессорах и изменчивой фоновой нагрузке активность окна не является основным фактором производительности; решающее значение имеют приоритет и распределение потоков планировщиком.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

children.push(heading("5. Задание 4. Влияние задержки 5 мс."));
children.push(body("В цикл каждого вычислительного потока добавлена задержка Sleep(5). Остальные условия соответствуют заданию 2."));
children.push(caption("Таблица 4 – Среднее число итераций за секунду с задержкой 5 мс"));
const rows4 = [-1, 0, 1].map(p => {
  const all = get("p4", false, p), one = get("p4", true, p);
  return [`${priorityName(p)}\n${priorityConst(p)}`, fmt2(all.avg1), fmt2(all.avg2), fmt2(one.avg1), fmt2(one.avg2)];
});
children.push(makeTable(["Приоритет потока 1", "Все ядра,\nпоток 1, 1/с", "Все ядра,\nпоток 2, 1/с", "Одно ядро,\nпоток 1, 1/с", "Одно ядро,\nпоток 2, 1/с"], rows4, [2200, 1700, 1700, 1700, 1700]));
children.push(...figure("graph_p4.png", 620, 1447, 808, "Рисунок 3 – Зависимость производительности от приоритета при задержке 5 мс"));
children.push(para([run("Вывод по эксперименту: ", { bold: true }), run("число итераций практически не зависит от приоритета и числа ядер и составляет 64,57–65,14 1/с. Потоки большую часть времени находятся в состоянии ожидания, поэтому не конкурируют за процессор. Полученная частота соответствует фактическому периоду ожидания около 15,4 мс, а не номинальным 5 мс.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

children.push(heading("6. Задание 5. Голодание и динамическое повышение приоритета."));
children.push(body("Первому потоку установлен приоритет THREAD_PRIORITY_LOWEST, второму — THREAD_PRIORITY_HIGHEST, процесс ограничен одним ядром. В таблице приведены все секундные измерения без усреднения. Первая секунда включает запуск и установку ограничения, поэтому не отражает установившийся режим."));
children.push(caption("Таблица 5 – Число итераций при приоритетах LOWEST и HIGHEST на одном ядре"));
children.push(makeTable(["Секунда", "Поток 1 (LOWEST), итераций", "Поток 2 (HIGHEST), итераций"],
  p5.map(r => [String(r[0]), fmtInt(r[1]), fmtInt(r[2])]), [1400, 3800, 3800]));
children.push(...figure("graph_p5.png", 620, 1453, 807, "Рисунок 4 – Голодание потока LOWEST и всплески его активности"));
children.push(para([run("Вывод по эксперименту: ", { bold: true }), run("со 2-й по 15-ю секунду первый поток большую часть времени получает 0 итераций, поскольку процессор занят потоком HIGHEST. В 7-ю секунду выполнены 38 953 итерации, а в 12-ю — 2 278 719 итераций. Эти кратковременные всплески показывают, что Windows динамически повышает приоритет длительно ожидающего потока и предотвращает его постоянное голодание.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

children.push(heading("7. Задание 6. Число потоков и загрузка процессора."));
children.push(body("Во время непрерывного запуска SPO_Lr3.exe с двумя потоками NORMAL получены сведения о процессе и сделан снимок Диспетчера задач. Число потоков подтверждено средствами Windows Get-Process, загрузка процесса оценена по приращению его процессорного времени за одну секунду."));
children.push(caption("Таблица 6 – Сведения о тестовом приложении"));
children.push(makeTable(["Показатель", "Значение"], [
  ["Идентификатор процесса", "22660"],
  ["Количество потоков", "3"],
  ["Логических процессоров в системе", "16"],
  ["Загрузка процессора процессом", "14,1 %"],
  ["Общая загрузка ЦП на снимке Диспетчера задач", "32 %"],
], [6000, 3000]));
children.push(para(new ImageRun({ type: "png", data: fs.readFileSync(path.join(root, "taskmanager.png")),
  transformation: { width: 620, height: 333 } }), { alignment: AlignmentType.CENTER, spacing: { before: 120, after: 0 }, keepNext: true }));
children.push(caption("Рисунок 5 – Диспетчер задач во время работы тестового приложения"));
children.push(para([run("Вывод по эксперименту: ", { bold: true }), run("процесс имеет ожидаемые три потока — главный и два дополнительных. Два вычислительных потока занимают примерно два логических процессора: 2 / 16 · 100 % = 12,5 % общей производительности; измеренные 14,1 % близки к этой оценке с учетом колебаний частоты и фоновой активности.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

children.push(heading("8. Исходный код тестового приложения."));
children.push(caption("Листинг 1 – Файл SPO_Lr3.cpp"));
for (const line of source.split("\n")) {
  children.push(new Paragraph({
    spacing: { after: 0, line: 220 },
    children: [new TextRun({ text: line || " ", font: codeFont, size: 18 })],
  }));
}

children.push(empty(120));
children.push(para([run("Вывод: ", { bold: true }), run("в ходе работы разработано приложение с тремя потоками, использующее Win32 API для создания потоков, изменения их приоритетов и измерения числа вычислительных итераций. Эксперименты показали, что приоритет существенно влияет на производительность при конкуренции за один процессор: повышение приоритета первого потока увеличивает его долю процессорного времени и уменьшает долю второго. При доступности нескольких ядер эта зависимость слабее и может маскироваться параллельным выполнением и фоновой нагрузкой. Задержка в цикле устраняет конкуренцию за процессор, поэтому влияние приоритета почти исчезает. При крайних приоритетах наблюдается голодание низкоприоритетного потока, периодически прерываемое динамическим повышением его приоритета. Критерием влияния приоритета на производительность является устойчивое различие числа итераций при одинаковой вычислительной работе и неизменных прочих условиях; наиболее явно оно проявляется при ограничении одним ядром и отсутствии задержек.")], { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 709 } }));

const doc = new Document({
  features: { updateFields: false },
  styles: { default: { document: { run: { font, size: 28 }, paragraph: { spacing: { after: 120, line: 276 } } } } },
  sections: [{
    properties: {
      titlePg: true,
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 850, bottom: 1134, left: 1701, header: 720, footer: 720 } },
    },
    footers: { default: new Footer({ children: [para(new TextRun({ children: [PageNumber.CURRENT], font, size: 24 }), { alignment: AlignmentType.CENTER })] }) },
    children,
  }],
});
fs.writeFileSync(outputPath, await Packer.toBuffer(doc));
