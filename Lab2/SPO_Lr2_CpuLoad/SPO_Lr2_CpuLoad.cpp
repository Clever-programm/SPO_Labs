// Лабораторная работа № 2. Монитор процессов и потоков.
// Индивидуальное задание 1 (вариант 10): загрузка процессора в процентах.

#include <windows.h>
#include <pdh.h>
#include <conio.h>
#include <cstdio>
#include <clocale>
#pragma comment(lib, "pdh.lib")

const int COUNT = 20;   // количество замеров (с интервалом 1 с)

// Добавление счетчика в запрос. Путь формируется функцией PdhMakeCounterPath
// из английских имен объекта, экземпляра и счетчика; PdhAddEnglishCounter
// принимает английские имена независимо от языка Windows.
bool AddCounter(PDH_HQUERY hQuery, const wchar_t* object, const wchar_t* instance,
    const wchar_t* counter, PDH_HCOUNTER* hCounter)
{
    PDH_COUNTER_PATH_ELEMENTS cpe = {};
    cpe.szMachineName = NULL;
    cpe.szObjectName = const_cast<wchar_t*>(object);
    cpe.szInstanceName = const_cast<wchar_t*>(instance);
    cpe.szParentInstance = NULL;
    cpe.dwInstanceIndex = 0;
    cpe.szCounterName = const_cast<wchar_t*>(counter);

    wchar_t path[PDH_MAX_COUNTER_PATH];
    DWORD size = PDH_MAX_COUNTER_PATH;
    PDH_STATUS status = PdhMakeCounterPath(&cpe, path, &size, 0);
    if (status == ERROR_SUCCESS)
        status = PdhAddEnglishCounter(hQuery, path, 0, hCounter);
    if (status != ERROR_SUCCESS)
    {
        wprintf_s(L"Не удалось добавить счетчик %s, код 0x%08lX\n", path, status);
        return false;
    }
    return true;
}

// Ожидание нажатия клавиши перед завершением программы
void WaitKey()
{
    wprintf_s(L"Нажмите любую клавишу для выхода...");
    _getch();
}

int main()
{
    setlocale(LC_CTYPE, "rus");

    PDH_HQUERY hQuery;
    PDH_HCOUNTER hProcessorTime, hProcessorUtility;

    if (PdhOpenQuery(NULL, 0, &hQuery) != ERROR_SUCCESS)
    {
        wprintf_s(L"Ошибка PdhOpenQuery\n");
        WaitKey();
        return 1;
    }

    // \Processor(_Total)\% Processor Time — загруженность процессора (все ядра)
    // \Processor Information(_Total)\% Processor Utility — значение, которое
    // показывает Диспетчер задач (учитывает текущую частоту процессора)
    if (!AddCounter(hQuery, L"Processor", L"_Total",
            L"% Processor Time", &hProcessorTime) ||
        !AddCounter(hQuery, L"Processor Information", L"_Total",
            L"% Processor Utility", &hProcessorUtility))
    {
        PdhCloseQuery(hQuery);
        WaitKey();
        return 1;
    }

    // Первый замер — базовый: значение счетчика вычисляется по двум замерам
    PdhCollectQueryData(hQuery);

    wprintf_s(L"Загрузка процессора: %d замеров с интервалом 1 с\n\n", COUNT);
    wprintf_s(L"%-10s %18s %20s\n", L"Время", L"% Processor Time", L"% Processor Utility");

    for (int i = 0; i < COUNT; i++)
    {
        Sleep(1000);
        PdhCollectQueryData(hQuery);

        PDH_FMT_COUNTERVALUE time = {}, utility = {};
        PDH_STATUS s1 = PdhGetFormattedCounterValue(hProcessorTime,
            PDH_FMT_DOUBLE, NULL, &time);
        PDH_STATUS s2 = PdhGetFormattedCounterValue(hProcessorUtility,
            PDH_FMT_DOUBLE, NULL, &utility);
        if (s1 != ERROR_SUCCESS || s2 != ERROR_SUCCESS)
            continue;

        // Utility может превышать 100% при турбо-частоте,
        // Диспетчер задач ограничивает его значением 100%
        double util = utility.doubleValue > 100.0 ? 100.0 : utility.doubleValue;

        SYSTEMTIME st;
        GetLocalTime(&st);
        wprintf_s(L"%02u:%02u:%02u   %16.1f %% %18.1f %%\n",
            st.wHour, st.wMinute, st.wSecond, time.doubleValue, util);
    }
    PdhRemoveCounter(hProcessorTime);
    PdhRemoveCounter(hProcessorUtility);
    PdhCloseQuery(hQuery);

    wprintf_s(L"\n");
    WaitKey();
    return 0;
}
