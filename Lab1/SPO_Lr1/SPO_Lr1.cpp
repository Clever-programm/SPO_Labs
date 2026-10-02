#include <iostream>
#include <cstdio>
#include <clocale>
#include <cstdlib>
using namespace std;

struct House
{
    char address[64];
    double area;
    int residents;
};

const int N = 5;

int main()
{
    setlocale(LC_CTYPE, "rus");

    // Задание 1
    int brigade;
    cout << "Введите номер бригады: ";
    cin >> brigade;
    if (!cin)
    {
        cout << "Ошибка ввода номера бригады" << endl;
        system("pause");
        return 1;
    }

    char student1[] = "Царегородцев";
    char student2[] = "Марченко";

    // Вывод с помощью потокового вывода cout
    cout << "\nБригада № " << brigade << endl;
    cout << student1 << endl;
    cout << student2 << endl;
    cout << endl;

    // Повтор вывода с помощью printf_s
    printf_s("Бригада № %d\n", brigade);
    printf_s("%s\n", student1);
    printf_s("%s\n", student2);
    printf_s("\n");

    int mas[3] = { 1, 2, 3 };
    int mmm[3] = { 4, 5, 6 };

    printf_s("\nmas: %d, %d, %d\n", mas[0], mas[1], mas[2]);
    printf_s("mmm: %d, %d, %d\n", mmm[0], mmm[1], mmm[2]);

    // Задание 2
    // Условие отбора: дом, в котором жилая площадь на одного жильца менее s
    House houses[N] =
    {
        { "ул. Молодогвардейская, 244", 3200.0, 120 },
        { "ул. Галактионовская, 141",   1500.0,  90 },
        { "пр. Ленина, 12",             2400.0,  60 },
        { "ул. Садовая, 5",              850.0,  50 },
        { "ул. Полевая, 18",            4100.0, 205 }
    };

    printf_s("\n\nСписок домов:\n");
    printf_s("%-3s %-30s %12s %10s %14s\n", "№", "Адрес", "Площадь", "Жильцов", "На 1 жильца");
    for (int i = 0; i < N; i++)
    {
        printf_s("%-3d %-30s %12.1f %10d %14.2f\n", i + 1, houses[i].address,
            houses[i].area, houses[i].residents, houses[i].area / houses[i].residents);
    }

    double s;
    cout << "\nВведите s (жилая площадь на одного жильца, кв. м): ";
    cin >> s;
    if (!cin)
    {
        cout << "Ошибка ввода s" << endl;
        system("pause");
        return 1;
    }

    FILE* f;
    const char* fname = "result.txt";
    if (fopen_s(&f, fname, "w") != 0)
    {
        printf_s("Ошибка открытия файла %s\n", fname);
        system("pause");
        return 1;
    }

    printf_s("\nДома, в которых жилая площадь на одного жильца менее %.2f кв. м:\n", s);
    fprintf_s(f, "Дома, в которых жилая площадь на одного жильца менее %.2f кв. м:\n", s);

    int found = 0;
    for (int i = 0; i < N; i++)
    {
        double perResident = houses[i].area / houses[i].residents;
        if (perResident < s)
        {
            printf_s("%-30s площадь %8.1f, жильцов %4d, на 1 жильца %6.2f\n",
                houses[i].address, houses[i].area, houses[i].residents, perResident);
            fprintf_s(f, "%-30s площадь %8.1f, жильцов %4d, на 1 жильца %6.2f\n",
                houses[i].address, houses[i].area, houses[i].residents, perResident);
            found++;
        }
    }

    if (found == 0)
    {
        printf_s("Таких домов нет\n");
        fprintf_s(f, "Таких домов нет\n");
    }

    fclose(f);
    printf_s("\nРезультат записан в файл %s\n", fname);

    system("pause");
    return 0;
}
