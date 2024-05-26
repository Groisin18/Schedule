import requests
import re
import json
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class Days:
    def __init__(self, date_: datetime):
        self.date_ = date_
        self.saints, self.service_options = self.find_saints_and_service()

    def save_page_in_file(self) -> None:
        '''
        Функция принимает дату в формате datetime и сохраняет страницу \n
        с сайта patriarchia.ru с Богослужеными указаниями\n
        в файл index.html
        '''
        url = f"http://www.patriarchia.ru/bu/{self.date_.strftime('%Y-%m-%d')}/"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537\
            .36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        headers = {
            "Accept": "*/*",
            "User-Agent": user_agent
        }

        req = requests.get(url, headers=headers)
        src = req.text
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(src)                        # Считывание страницы в файл

        return None


    def find_saints_and_service(self) -> tuple:
        '''
        Функция возвращает кортеж:\n
        (празднуемые святые, какая служба будет служиться),\n
        используя информацию из файла index.html
        '''
        soup = self.save_page_in_file() # сохраняем страницу Богослужебных
                                    # указаний на данный день в файл index.html

        with open("index.html", encoding="utf-8") as file:
            src = file.read()                           # Создание объекта soup
        soup = BeautifulSoup(src, "lxml")

        in_day_head = soup.find(class_ = "ln-day-head").text  # Находим
                 # заголовок с перечислением святых, празднующихся в этот день
        saints = in_day_head[
            in_day_head.find(". ", in_day_head.find(". ")+1)+2:
            ]                          # Отсекаем в строчке число и день недели

                        # Надо сделать отдельную обработку для воскресений

        service_options = soup.find(string=re.compile("Служба", re.I))
                                                # Ищем богослужебные указания
        if service_options is None:
            service_options = soup.find(string=re.compile("Службы", re.I))

        if service_options is None:
            service_options = soup.find(string=re.compile("Бдение", re.I))

    # Надо сделать обработку случая, когда слово "служба" встречается в примечании
    # div class='ln-emb-note'
        return (saints, service_options)


def test_period (day: int, month: int, year: int, count_days: int) -> list:
    '''
    НЕ РАБОТАЕТ
        Функция принимает день, месяц, год и количество дней,\n
        и тестирует функцию find_saint_and_service()\n
        на count_days днях, начиная с передаваемой в функцию даты
    '''
    pass
    # date_for_test = datetime(year, month, day)
    # delta = timedelta(days=1)
    # Errors_list = []

    # for _ in range(count_days):
    #     try:
    #         saint_and_service = Days.find_saints_and_service(date_for_test)
    #         str_date = date_for_test.strftime('%d.%m.%Y')
    #         if saint_and_service[1] is None:
    #             print(f"Ошибка при обработке указаний даты {str_date}")
    #             Errors_list.append(str_date)
    #         else:
    #             print(f"Дата {str_date} отработана корректно")
    #     except (
    #         TimeoutError, ConnectionError, requests.exceptions.ConnectTimeout
    #         ):
    #         print(f"Ошибка соединения с сайтом при обработке даты {str_date}")
    #         Errors_list.append(str_date)
    #         print("Пробуем снова...")
    #         saint_and_service = find_saint_and_service(date_for_test)
    #         if saint_and_service[1] is None:
    #             print(f"Повторная ошибка при обработке даты {str_date}")
    #         else:
    #             Errors_list.remove(str_date)
    #             print(f"Дата {str_date} отработана корректно")
    #     date_for_test += delta
    # return Errors_list if Errors_list else "Ошибок не найдено"


def add_data_into_json(date_: datetime, file_name: str):
    '''
    Функция принимает дату в формате datetime и имя файла\n
    формирует json-файл "file_name.json", если такого еще нет,\n
    либо открывает уже существующий; и добавляет в него данные:\n
    "дата": [празднуемые святые, какая служба будет служиться]
    '''
    day_ = Days(date_)
    str_date = datetime.strftime(day_.date_, "%d.%m.%Y")
    with open(file_name, "a", encoding="utf-8") as file:
        json.dump({str_date: [day_.saints, day_.service_options]}, file)

def add_data_into_csv(date_: datetime, file_name: str):
    '''
    Функция принимает дату в формате datetime и имя файла\n
    формирует csv-файл "file_name.csv", если такого еще нет,\n
    либо открывает уже существующий; и добавляет в него данные:\n
    (дата; празднуемые святые; какая служба будет служиться)
    '''
    day_ = Days(date_)
    str_date = datetime.strftime(day_.date_, "%d.%m.%Y")
    with open(file_name, "a", encoding="utf-8") as file:
        columns = ("date", "saints", "service_options")
        writer = csv.writer(file, delimiter=';')
        if os.stat(file_name).st_size == 0:
            writer.writerow(columns)
        writer.writerow((str_date, day_.saints, day_.service_options))


delta = timedelta(1)
st_date = datetime(2024, 5, 27)
for i in range(10):
    add_data_into_csv(st_date, "test1.csv")
    st_date += delta
