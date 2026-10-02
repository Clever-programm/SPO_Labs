#include <windows.h>
#include <lmcons.h>
#include <cstdio>
#include <clocale>
#include <cstdlib>

int main()
{
    setlocale(LC_CTYPE, "rus");

    // Имя пользователя
    TCHAR userName[UNLEN + 1];
    DWORD userSize = _countof(userName);
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

    system("pause");
    return 0;
}
