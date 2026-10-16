// Лабораторная работа № 2. Монитор процессов и потоков.
// Индивидуальное задание 2 (вариант 10): список прикладных процессов,
// использующих более M байт оперативной памяти.

#include <windows.h>
#include <tlhelp32.h>
#include <psapi.h>
#include <iostream>
#include <cstdio>
#include <clocale>
#include <conio.h>
#pragma comment(lib, "psapi.lib")
using namespace std;

struct ProcInfo
{
    PROCESSENTRY32 pe;      // сведения о процессе из снимка
    SIZE_T workingSet;      // объем используемой оперативной памяти (рабочий набор), байт
};

const int MAX_PROC = 1024;
ProcInfo procList[MAX_PROC];    // процессы, удовлетворяющие условию отбора

// Ожидание нажатия клавиши перед завершением программы
void WaitKey()
{
    wprintf_s(L"Нажмите любую клавишу для выхода...");
    _getch();
}

int main()
{
    setlocale(LC_CTYPE, "rus");

    unsigned long long M;
    wprintf_s(L"Введите M (байт): ");
    if (!(cin >> M))
    {
        wprintf_s(L"Ошибка ввода M\n");
        WaitKey();
        return 1;
    }

    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnap == INVALID_HANDLE_VALUE)
    {
        wprintf_s(L"Ошибка CreateToolhelp32Snapshot, код %lu\n", GetLastError());
        WaitKey();
        return 1;
    }

    int count = 0;              // количество отобранных процессов
    int appCount = 0;           // количество просмотренных прикладных процессов

    PROCESSENTRY32 pe;
    pe.dwSize = sizeof(PROCESSENTRY32);
    if (Process32First(hSnap, &pe))
    {
        do
        {
            // Службы и системные процессы выполняются в сеансе 0,
            // прикладные процессы пользователя — в сеансах 1, 2, ...
            DWORD session;
            if (!ProcessIdToSessionId(pe.th32ProcessID, &session) || session == 0)
                continue;

            HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE,
                pe.th32ProcessID);
            if (hProc == NULL)
                continue;

            PROCESS_MEMORY_COUNTERS pmc;
            if (GetProcessMemoryInfo(hProc, &pmc, sizeof(pmc)))
            {
                appCount++;
                if (pmc.WorkingSetSize > M && count < MAX_PROC)
                {
                    procList[count].pe = pe;
                    procList[count].workingSet = pmc.WorkingSetSize;
                    count++;
                }
            }
            CloseHandle(hProc);
        } while (Process32Next(hSnap, &pe));
    }
    CloseHandle(hSnap);

    // Сортировка выбором по убыванию используемой памяти
    for (int i = 0; i < count - 1; i++)
    {
        int maxIndex = i;
        for (int j = i + 1; j < count; j++)
        {
            if (procList[j].workingSet > procList[maxIndex].workingSet)
                maxIndex = j;
        }
        if (maxIndex != i)
        {
            ProcInfo tmp = procList[i];
            procList[i] = procList[maxIndex];
            procList[maxIndex] = tmp;
        }
    }

    wprintf_s(L"\nПрикладные процессы, использующие более %llu байт (%.1f МБ) "
        L"оперативной памяти:\n\n", M, M / 1048576.0);
    wprintf_s(L"%8s  %-32s %16s %10s\n", L"PID", L"Имя процесса", L"Память, байт", L"МБ");
    for (int i = 0; i < count; i++)
    {
        wprintf_s(L"%8lu  %-32s %16zu %10.1f\n",
            procList[i].pe.th32ProcessID, procList[i].pe.szExeFile,
            procList[i].workingSet, procList[i].workingSet / 1048576.0);
    }
    wprintf_s(L"\nНайдено процессов: %d (из %d прикладных)\n\n", count, appCount);

    WaitKey();
    return 0;
}
