import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

def parse_page(date_: datetime) -> None:
    '''
    Функция принимает дату в формате datetime и парсит страницу \n
    с сайта patriarchia.ru с Богослужеными указаниями\n
    в файл index.html
    '''
    url = f"http://www.patriarchia.ru/bu/{date_.strftime('%Y-%m-%d')}/"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    headers = {
        "Accept": "*/*",
        "User-Agent": user_agent
    }

    req = requests.get(url, headers=headers)
    src = req.text
    with open("index.html", "w", encoding="utf-8") as file:  
        file.write(src)                             # Считывание страницы в файл

    return None


def find_saint_and_service(date_: datetime) -> tuple:
    '''
    Функция принимает дату в формате datetime и возвращает кортеж:\n
    (дата, празднуемые святые, какая служба будет служиться),\n
    используя информацию с сайта patriarchia.ru
    '''
    soup = parse_page(date_) # парсим страницу Богослужебных указаний 
                                               #на данный день в файл index.html

    with open("index.html", encoding="utf-8") as file: # Создание объекта soup
        src = file.read()
    soup = BeautifulSoup(src, "lxml") 

    in_day_head = soup.find(class_ = "ln-day-head").text  # Находим заголовок с 
                               # перечислением святых, празднующихся в этот день
    in_day_head = in_day_head[
        in_day_head.find(". ", in_day_head.find(". ")+1)+2:
        ]                               # Отсекаем в строчке число и день недели

                              # Надо сделать отдельную обработку для воскресений

    service_options = soup.find(text=re.compile("Служба", re.I))
                                                   # Ищем богослужебные указания
    if service_options is None:
        service_options = soup.find(text=re.compile("Службы", re.I))
    
    if service_options is None:
        service_options = soup.find(text=re.compile("Бдение", re.I))

# Надо сделать обработку случая, когда слово "служба" встречается в примечании
# div class='ln-emb-note'
    str_date = date_.strftime('%d.%m.%Y')
    return (str_date, in_day_head, service_options)


def test_period (day: int, month: int, year: int, count_days: int) -> list:
    '''
        Функция тестирует функцию find_saint_and_service()\n
        на семи днях, начиная с передаваемой в функцию даты
    '''

    date_for_test = datetime(year, month, day)
    delta = timedelta(days=1)
    Errors_list = []

    for _ in range(count_days):
        try:
            saint_and_service = find_saint_and_service(date_for_test)
            str_date = date_for_test.strftime('%d.%m.%Y')
            if saint_and_service[1] is None:
                print(f"Ошибка при обработке указаний даты {str_date}")
                Errors_list.append(str_date)
            else:
                print(f"Дата {str_date} отработана корректно")
        except (
            TimeoutError, ConnectionError, requests.exceptions.ConnectTimeout
            ):
            print(f"Ошибка соединения с сайтом при обработке даты {str_date}")
            Errors_list.append(str_date)
            print("Пробуем снова...")
            saint_and_service = find_saint_and_service(date_for_test)
            if saint_and_service[1] is None:
                print(f"Повторная ошибка при обработке даты {str_date}")
            else:
                Errors_list.remove(str_date)
                print(f"Дата {str_date} отработана корректно")
        date_for_test += delta
    return Errors_list if Errors_list else "Ошибок не найдено"


def add_data_into_json(date_: datetime):
    '''
    Функция принимает дату в формате datetime,\n
    формирует json-файл "data.json", если такого еще нет,\n
    либо открывает уже существующий; и добавляет в него данные:\n
    "дата": [празднуемые святые, какая служба будет служиться],\n
    взятые из функции find_saint_and_service(date_)
    '''
    data = find_saint_and_service(date_)
    with open("data.json", "a", encoding="utf-8") as file:
        json.dump({data[0]: [data[1], data[2]]}, file)


with open("test_year_1.html", "w", encoding="utf-8") as file:
    file.writelines(test_period(1, 1, 2024, 365))