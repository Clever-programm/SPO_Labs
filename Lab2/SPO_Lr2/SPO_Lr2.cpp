// Лабораторная работа № 2. Монитор процессов и потоков.
// Базовые задания: список процессов, приоритет и количество потоков процесса,
// время работы процесса в режиме ядра и в режиме пользователя.

#include <windows.h>
#include <tlhelp32.h>
#include <iostream>
#include <cstdio>
#include <conio.h>
#include <clocale>
using namespace std;

// Ожидание нажатия клавиши перед завершением программы
void WaitKey()
{
    wprintf_s(L"Нажмите любую клавишу для выхода...");
    _getch();
}

// Ввод идентификатора процесса с клавиатуры
DWORD ReadPid(const wchar_t* prompt)
{
    DWORD pid;
    while (true)
    {
        wprintf_s(L"%s", prompt);
        if (cin >> pid)
            return pid;
        wprintf_s(L"Ошибка ввода, повторите\n");
        cin.clear();
        cin.ignore(10000, '\n');
    }
}

// Задание 1. Вывод списка процессов, выполняющихся в системе
void PrintProcessList()
{
    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnap == INVALID_HANDLE_VALUE)
    {
        wprintf_s(L"Ошибка CreateToolhelp32Snapshot, код %lu\n", GetLastError());
        return;
    }

    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(PROCESSENTRY32);
    int count = 0;

    wprintf_s(L"%8s %8s %7s %10s  %s\n",
        L"PID", L"PPID", L"Потоков", L"Приоритет", L"Имя процесса");
    if (Process32First(hSnap, &pe))
    {
        do
        {
            wprintf_s(L"%8lu %8lu %7lu %10ld  %s\n", pe.th32ProcessID, pe.th32ParentProcessID,
                pe.cntThreads, pe.pcPriClassBase, pe.szExeFile);
            count++;
        } while (Process32Next(hSnap, &pe));
    }
    CloseHandle(hSnap);

    wprintf_s(L"Всего процессов: %d\n", count);
}

// Поиск процесса в снимке по идентификатору
bool FindProcess(DWORD pid, PROCESSENTRY32& pe)
{
    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnap == INVALID_HANDLE_VALUE)
        return false;

    bool found = false;
    pe.dwSize = sizeof(PROCESSENTRY32);
    if (Process32First(hSnap, &pe))
    {
        do
        {
            if (pe.th32ProcessID == pid)
            {
                found = true;
                break;
            }
        } while (Process32Next(hSnap, &pe));
    }
    CloseHandle(hSnap);
    return found;
}

// Название класса приоритета процесса
const wchar_t* PriorityClassName(DWORD priorityClass)
{
    switch (priorityClass)
    {
    case IDLE_PRIORITY_CLASS:         return L"IDLE (низкий)";
    case BELOW_NORMAL_PRIORITY_CLASS: return L"BELOW_NORMAL (ниже среднего)";
    case NORMAL_PRIORITY_CLASS:       return L"NORMAL (обычный)";
    case ABOVE_NORMAL_PRIORITY_CLASS: return L"ABOVE_NORMAL (выше среднего)";
    case HIGH_PRIORITY_CLASS:         return L"HIGH (высокий)";
    case REALTIME_PRIORITY_CLASS:     return L"REALTIME (реального времени)";
    default:                          return L"неизвестен";
    }
}

// Задание 2. Приоритет и количество потоков выбранного процесса
void PrintPriorityAndThreads(DWORD pid)
{
    PROCESSENTRY32 pe;
    if (!FindProcess(pid, pe))
    {
        wprintf_s(L"Процесс с PID %lu не найден\n", pid);
        return;
    }

    wprintf_s(L"\nПроцесс: %s (PID %lu)\n", pe.szExeFile, pid);
    wprintf_s(L"Базовый приоритет:  %ld\n", pe.pcPriClassBase);

    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (hProc != NULL)
    {
        wprintf_s(L"Класс приоритета:   %s\n", PriorityClassName(GetPriorityClass(hProc)));
        CloseHandle(hProc);
    }
    wprintf_s(L"Количество потоков: %lu\n", pe.cntThreads);

    // Список потоков процесса с их приоритетами
    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0);
    if (hSnap == INVALID_HANDLE_VALUE)
        return;

    THREADENTRY32 te;
    te.dwSize = sizeof(THREADENTRY32);
    int n = 0;
    wprintf_s(L"\nПотоки процесса (ID потока: приоритет):\n");
    if (Thread32First(hSnap, &te))
    {
        do
        {
            if (te.th32OwnerProcessID == pid)
            {
                wprintf_s(L"%8lu: %-4ld", te.th32ThreadID, te.tpBasePri);
                if (++n % 6 == 0)
                    wprintf_s(L"\n");
            }
        } while (Thread32Next(hSnap, &te));
    }
    CloseHandle(hSnap);
    if (n % 6 != 0)
        wprintf_s(L"\n");
}

// Перевод времени FILETIME (интервалы по 100 нс) в миллисекунды
ULONGLONG FileTimeToMs(const FILETIME& ft)
{
    ULARGE_INTEGER t;
    t.LowPart = ft.dwLowDateTime;
    t.HighPart = ft.dwHighDateTime;
    return t.QuadPart / 10000;
}

// Вывод длительности в формате чч:мм:сс.мс
void PrintDuration(const wchar_t* title, const FILETIME& ft)
{
    ULONGLONG ms = FileTimeToMs(ft);
    wprintf_s(L"%s %02llu:%02llu:%02llu.%03llu (%.3f с)\n", title,
        ms / 3600000, ms / 60000 % 60, ms / 1000 % 60, ms % 1000, ms / 1000.0);
}

// Задание 3. Время работы процесса в режиме ядра и в режиме пользователя
void PrintProcessTimes(DWORD pid)
{
    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (hProc == NULL)
    {
        DWORD err = GetLastError();
        wprintf_s(L"Не удалось открыть процесс %lu, код ошибки %lu\n", pid, err);
        if (err == ERROR_ACCESS_DENIED)
            wprintf_s(L"Доступ запрещен: это системный процесс, выберите прикладной\n");
        else if (err == ERROR_INVALID_PARAMETER)
            wprintf_s(L"Процесс с таким PID не существует\n");
        return;
    }

    FILETIME ftCreation, ftExit, ftKernel, ftUser;
    if (!GetProcessTimes(hProc, &ftCreation, &ftExit, &ftKernel, &ftUser))
    {
        wprintf_s(L"Ошибка GetProcessTimes, код %lu\n", GetLastError());
        CloseHandle(hProc);
        return;
    }
    CloseHandle(hProc);

    // Время запуска: UTC -> местное время -> SYSTEMTIME
    FILETIME ftLocal;
    SYSTEMTIME st;
    FileTimeToLocalFileTime(&ftCreation, &ftLocal);
    FileTimeToSystemTime(&ftLocal, &st);

    wprintf_s(L"\nВремя запуска процесса:        %02u.%02u.%04u %02u:%02u:%02u\n",
        st.wDay, st.wMonth, st.wYear, st.wHour, st.wMinute, st.wSecond);
    PrintDuration(L"Время в режиме ядра:          ", ftKernel);
    PrintDuration(L"Время в режиме пользователя:  ", ftUser);
}

int main()
{
    setlocale(LC_CTYPE, "rus");

    wprintf_s(L"=== Задание 1. Список процессов ===\n\n");
    PrintProcessList();

    wprintf_s(L"\n=== Задание 2. Приоритет и количество потоков процесса ===\n");
    PrintPriorityAndThreads(ReadPid(L"Введите PID процесса: "));

    wprintf_s(L"\n=== Задание 3. Время работы процесса в режимах ядра и пользователя ===\n");
    PrintProcessTimes(ReadPid(L"Введите PID прикладного процесса: "));

    wprintf_s(L"\n");
    WaitKey();
    return 0;
}
