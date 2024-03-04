import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def find_saint_and_service(date_: datetime) -> tuple:

    url = f"http://www.patriarchia.ru/bu/{date_.strftime('%Y-%m-%d')}/"
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    req = requests.get(url, headers=headers)
    src = req.text
    with open("index.html", "w", encoding="utf-8") as file:  # Считывание страницы в файл
        file.write(src)

    with open("index.html", encoding="utf-8") as file: # Создание объекта soup
        src = file.read()
    soup = BeautifulSoup(src, "lxml") 

    title = soup.title.string

    in_day_head = soup.find(class_ = "ln-day-head").text  # Находим заголовок с перечислением святых, празднующихся в этот день
    in_day_head = in_day_head[in_day_head.find(". ", in_day_head.find(". ")+1)+2:]  # Отсекаем в строчке число и день недели

    service_options = soup.find("p", string=re.compile("Служба|cлужба")).text # Ищем богослужебные указания

    return (title, in_day_head, service_options)

def test_week (day: int, month: int, year: int) -> list:
    date_for_test = datetime(year, month, day)
    delta = timedelta(days=1)
    Errors_list = []
    for i in range(7):
        try:
            date_for_test += delta
            print(find_saint_and_service(date_for_test))
        except AttributeError:
            error_date = date_for_test.strftime('%d.%m.%Y')
            Errors_list.append(error_date)
            print(f"Ошибка при обработке даты {error_date}")

    return Errors_list

print(test_week(4, 3, 2024))
