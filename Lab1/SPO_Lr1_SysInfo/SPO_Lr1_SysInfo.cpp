// Лабораторная работа № 1. Функции получения системной информации.
// Задание 3, вариант 1: имя пользователя, имя компьютера.

#include <windows.h>
#include <lmcons.h>     // UNLEN — максимальная длина имени пользователя
#include <cstdio>
#include <clocale>

int main()
{
    setlocale(LC_CTYPE, "rus");     // русификация вывода

    // Имя пользователя
    TCHAR userName[UNLEN + 1];
    DWORD userSize = _countof(userName);    // размер буфера в символах
    if (GetUserName(userName, &userSize))
        wprintf_s(L"Имя пользователя: %s\n", userName);
    else
        wprintf_s(L"Ошибка GetUserName, код %lu\n", GetLastError());

    // Имя компьютера
    TCHAR computerName[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD computerSize = _countof(computerName);
    if (GetComputerName(computerName, &computerSize))
        wprintf_s(L"Имя компьютера:   %s\n", computerName);
    else
        wprintf_s(L"Ошибка GetComputerName, код %lu\n", GetLastError());

    return 0;
}
