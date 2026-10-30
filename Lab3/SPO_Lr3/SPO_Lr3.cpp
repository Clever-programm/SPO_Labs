// Лабораторная работа № 3. Процессы и потоки.
// Исследование диспетчеризации потоков.

#include <windows.h>
#include <cstdio>
#include <cstdlib>
#include <clocale>
#include <cmath>

struct ThreadData
{
    int priority;              // относительный приоритет потока
    DWORD delay;               // задержка в каждом цикле, мс
    volatile LONG count;       // число итераций за текущую секунду
    volatile BOOL finish;      // признак завершения потока
    double result;             // результат вычислений (не дает удалить их оптимизатору)
};

// Функция дополнительного потока: непрерывное вычисление тригонометрического выражения
DWORD WINAPI CalculationThread(LPVOID lpParam)
{
    ThreadData* data = (ThreadData*)lpParam;
    SetThreadPriority(GetCurrentThread(), data->priority);

    double x = 0.0;
    double y = 0.0;
    while (!data->finish)
    {
        x += 0.000001;
        y += sin(x) * cos(x);
        InterlockedIncrement(&data->count);
        if (data->delay != 0)
            Sleep(data->delay);
    }
    data->result = y;
    return 0;
}

const char* PriorityName(int priority)
{
    switch (priority)
    {
    case THREAD_PRIORITY_LOWEST:       return "LOWEST";
    case THREAD_PRIORITY_BELOW_NORMAL: return "BELOW_NORMAL";
    case THREAD_PRIORITY_NORMAL:       return "NORMAL";
    case THREAD_PRIORITY_ABOVE_NORMAL: return "ABOVE_NORMAL";
    case THREAD_PRIORITY_HIGHEST:      return "HIGHEST";
    default:                           return "UNKNOWN";
    }
}

int main(int argc, char* argv[])
{
    setlocale(LC_CTYPE, "rus");
    if (argc > 5)
        SetConsoleTitleA(argv[5]);

    // Аргументы: приоритет 1, приоритет 2, задержка (мс), длительность (с).
    // Нулевая длительность означает работу до закрытия окна или Ctrl+C.
    int priority1 = argc > 1 ? atoi(argv[1]) : THREAD_PRIORITY_NORMAL;
    int priority2 = argc > 2 ? atoi(argv[2]) : THREAD_PRIORITY_NORMAL;
    DWORD delay = argc > 3 ? (DWORD)atoi(argv[3]) : 0;
    int duration = argc > 4 ? atoi(argv[4]) : 0;

    ThreadData data1 = { priority1, delay, 0, FALSE, 0.0 };
    ThreadData data2 = { priority2, delay, 0, FALSE, 0.0 };

    HANDLE h1 = CreateThread(NULL, 0, CalculationThread, &data1, 0, NULL);
    HANDLE h2 = CreateThread(NULL, 0, CalculationThread, &data2, 0, NULL);
    if (h1 == NULL || h2 == NULL)
    {
        printf_s("Ошибка CreateThread, код %lu\n", GetLastError());
        return 1;
    }

    printf_s("SPO_Lr3, PID=%lu\n", GetCurrentProcessId());
    printf_s("Поток 1: %s (%d); поток 2: %s (%d); задержка: %lu мс\n",
        PriorityName(priority1), priority1, PriorityName(priority2), priority2, delay);
    printf_s("Секунда;Итерации потока 1;Итерации потока 2\n");

    long long sum1 = 0, sum2 = 0;
    int second = 1;
    while (duration == 0 || second <= duration)
    {
        Sleep(1000);
        LONG count1 = InterlockedExchange(&data1.count, 0);
        LONG count2 = InterlockedExchange(&data2.count, 0);
        printf_s("%d;%ld;%ld\n", second, count1, count2);
        fflush(stdout);
        sum1 += count1;
        sum2 += count2;
        second++;
    }

    data1.finish = TRUE;
    data2.finish = TRUE;
    WaitForSingleObject(h1, INFINITE);
    WaitForSingleObject(h2, INFINITE);
    CloseHandle(h1);
    CloseHandle(h2);

    int measured = second - 1;
    if (measured > 0)
    {
        printf_s("Среднее;%.1f;%.1f\n", (double)sum1 / measured, (double)sum2 / measured);
        printf_s("Результаты вычислений: %.3f; %.3f\n", data1.result, data2.result);
    }
    return 0;
}
