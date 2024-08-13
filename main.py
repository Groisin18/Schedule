import requests, re, json, csv, os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Literal

class Days:
    def __init__(self, date_: datetime):
        self.date_ = date_
        self.saints, self.service_options = self.find_saints_and_service()
        self.signs = self.discover_sign()

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

    def prepare_index_for_work(self):
        '''
        Функция сохраняет страницу и готовит ее для последующей обработки
        '''
        self.save_page_in_file() # сохраняем страницу Богослужебных
                                 # указаний на данный день в файл index.html

        with open("index.html", encoding="utf-8") as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")

        # обрезка index.html только до нужного div'a
        soup = soup.find('div', id = "main")
        soup = soup.find('div', class_ = "section")

        # устраняем ошибку с неверным определением богослужебных указаний
        str_for_delete = soup.find(string=re.compile('может быть перенесена', re.I))
        if str_for_delete:
            str_for_delete.extract()

# str_for_delete = soup.find(string=re.compile('переносится', re.I))
# if str_for_delete:
#     str_for_delete.extract()

        # отсекаем все примечания, которые могут мешаться
        for i in range(5):
            str_for_delete = soup.find(id="ln-note-ref-" + str(i))
            if str_for_delete:
                str_for_delete.parent.extract()

        with open('index.html', 'w', encoding="utf-8") as f:
            f.write(soup.prettify())

    def find_saints_and_service(self) -> tuple:
        '''
        Функция возвращает кортеж:\n
        (празднуемые святые, какая служба будет служиться),\n
        используя информацию из файла index.html
        '''
        self.prepare_index_for_work()

        with open("index.html", encoding="utf-8") as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")

        # Находим заголовок с перечислением святых, празднующихся в этот день
        in_day_head = soup.find(class_ = "ln-day-head").text
        # Отсекаем в строчке число и день недели
        saints = in_day_head[
            in_day_head.find(". ", in_day_head.find(". ")+1)+2:
            ].strip()

        service_options = []
        # Обработка воскресений
        if self.date_.weekday() == 6:
            saints = saints[saints.find('. ')+2:]
            service_options.append('Совершается всенощное бдение (воскресение)')
            return (saints, service_options)

        def find_variant_in_all_index():
            '''Функция ищет богослужебные указания в файле index.html
            и добавляет их в self.service_options
            '''
            with open("index.html", encoding="utf-8") as file:
                src = file.read()
                soup = BeautifulSoup(src, "lxml")
            service_option = soup.find(string=re.compile('совершается всенощное',
                                                      re.I))
            if  service_option is None:
                service_option = soup.find(string=re.compile("Служба", re.I))
                if service_option is None:
                    service_option = soup.find(string=re.compile("Службы", re.I))
                    if service_option is None:
                        service_option = soup.find(string=re.compile("Бдение", re.I))
            service_options.append(service_option.strip())

    # Проверяем, есть ли разные варианты службы в указаниях, добавляем их в
    # список вариантов
        possible_variants = ['A', 'B', 'C', 'D']
        for i in possible_variants:
            variant = soup.find(id = ("ln-nav-ref-" + i))
            if variant:
                service_options.append(variant.parent.previous_sibling.strip())
            else:
                if not service_options:
                    find_variant_in_all_index()
                break

        return (saints, service_options)

    possible_signs = Literal[
                'Не определен', 'Аллилуия' 'Вседневная', 'Шестеричная', 'Славословная',
                 'Полиелей', 'Бдение', 'Двунадесятый'
                 ]
    def discover_sign(self) -> list[possible_signs]:
        '''
        Функция возвращает список с вариантами знака службы
        '''
        result = []
        for i in self.service_options:
            if 'аллилуйная' in i:
                result.append("Аллилуия")
            if 'не имеет праздничного знака' in i:
                result.append("Вседневная")
            if 'шестеричн' in i:
                result.append("Шестеричная")
            if 'лавословн' in i:
                result.append("Славословная")
            if 'полиелей' in i or 'Полиелей' in i:
                result.append("Полиелей")
            if 'Бден' in i or 'бден' in i:
                result.append("Бдение")
            if not result:
                result.append('Не определен')
        return result


    def add_data_into_json(self, file_name: str):
        '''
        Функция принимает дату в формате datetime и имя файла\n
        формирует json-файл "file_name.json", если такого еще нет,\n
        либо открывает уже существующий; и добавляет в него данные:\n
        "дата": [празднуемые святые, какая служба будет служиться, знак службы]
        '''

        str_date = datetime.strftime(self.date_, "%d.%m.%Y")
        with open(file_name, "a", encoding="utf-8") as file:
            json.dump({str_date: [self.saints, self.service_options,
                                  self.signs]}, file)


    def add_data_into_csv(self, file_name: str):
        '''
        Функция принимает дату в формате datetime и имя файла\n
        формирует csv-файл "file_name.csv", если такого еще нет,\n
        либо открывает уже существующий; и добавляет в него данные:\n
        (дата; празднуемые святые; какая служба будет служиться, знак службы)
        '''
        str_date = datetime.strftime(self.date_, "%d.%m.%Y")
        with open(file_name, "a", encoding="utf-8") as file:
            columns = ("date", "saints", "service_options")
            writer = csv.writer(file, delimiter=';')
            if os.stat(file_name).st_size == 0:
                writer.writerow(columns)
            writer.writerow((str_date, self.saints, self.service_options,
                             self.signs))



def make_file_for_period (count_days: int) -> list:
    '''
    НЕ РАБОТАЕТ (но хранит полезный код)
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


st_date = datetime(2024, 1, 1)
for i in range(100):
    delta = timedelta(i)
    day = Days(st_date + delta)
    if day.signs[0] == 'Не определен':
        print(st_date + delta)
        day.add_data_into_csv("test_file_1.csv")

    '''
    На примере 23 января 2024 надо посмотреть, что делать с вариантом
    "Приводим также порядок совершения полиелейной или бденной службы"

    Надо посмотреть, нужны ли строчки 50-52 (закомментированное обрезание)

    # Надо сделать обработку случая, когда слово "служба" встречается в примечании
    # div class='ln-emb-note'

    Огромная работа для великого поста
    '''
