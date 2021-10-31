import gspread
import re
import time

link_spec = (r'https://docs.google.com/spreadsheets/d/'
             r'1bpBdAVG7p523vIoR7hyarcfmIUHbmr73tULR8D3m7E8/htmlview#gid=125567056')

link_barrister = (
    r'https://docs.google.com/spreadsheets/d/1pr8iciZDleqacIbg2b9fUxt_712i3HYqCITFKqs82Wg/edit#gid=42475339')


class Changer:
    def __init__(self, link, data: list):
        self._service_account = 'my-test-project-315517-4842cc3c8961.json'
        self._link = link
        self.get_data_name = data[0]
        self.get_data_end_day = data[1]
        self.person_list = self.get_values()
        self.hours_list = self.calculate()
        self.last_int_in_sheets = len(self.hours_list)
        # Получаем рабочее пространство

    # Получаем список из таблицы в интернете
    def get_values(self):
        self.gc = gspread.service_account(filename=self._service_account)
        self.sh = self.gc.open_by_url(self._link)
        self.worksheet = self.sh.get_worksheet(0)

        list_of_personal = self.worksheet.get_all_values()

        # С помощью среза выбираем только строки начинающиеся с имени, заканчивающие сменой в воскресенье
        list_of_personal = [
            data[int(f'{self.get_data_name}'):int(f'{self.get_data_end_day}')] if len(
                data[int(f'{self.get_data_name}')]) > 6 else [] for data in list_of_personal]

        # Убираем в списке пустые элементы
        list_of_personal = [[el for el in values if el] for values in list_of_personal]

        # В целях производительности, пожертвовал читабельностью, заменил циклы на list comprehension
        # Здесь, с помощью регулярного выражения собираются в списке только цифры и знак "-"
        hours_of_person_on_week = [[''.join(re.findall(r'[0-9-.]+', values.replace(':', '.'))) for values in el]
                                   for el in [el[1:] for el in list_of_personal]]

        # Собираем список, где 1-й элемент - имя, остальное - часы
        list_of_personal = [[list_of_personal[i][0]] + hours_of_person_on_week[i]
                            if list_of_personal[i] else [] for i in range(len(list_of_personal))]
        return list_of_personal

    # Функция для подсчета времени в списках (возвращает список подсчитанных часов во всех строках)
    def calculate(self):
        list_of_time = []
        for el in self.person_list:
            hours_list = el[1:]
            # Пустой список, для сложения всех секунд на рабочей неделе
            sum_seconds_on_week = []
            # Проходимся по каждому значению в списках
            for ej in hours_list:
                # Получаем 2 вложенных списка [[],[]]
                hours = list(map(lambda a: (str(float('0' + a)) + '0').split('.'), ej.split('-')))
                # Проверяем, действительно ли получилось 2 вложеннных списка
                if len(hours) == 2:
                    # Получаем время в секундах у первого вложенного списка(1-й элемент всегда час, второй - минута
                    first_list_in_sec = int(hours[0][0]) * 3600 + int(hours[0][1]) * 60
                    # Получаем время в секундах у второго вложенного списка(1-й элемент всегда час, второй - минута
                    second_list_in_sec = int(hours[1][0]) * 3600 + int(hours[1][1]) * 60

                    if float(hours[0][0]) < float(hours[1][0]):
                        day_shift = second_list_in_sec - first_list_in_sec
                        sum_seconds_on_week.append(day_shift)
                    else:
                        night_shift = (24 * 3600 - first_list_in_sec) + second_list_in_sec
                        sum_seconds_on_week.append(float(night_shift))

            list_of_time.append(format_seconds(sum(sum_seconds_on_week)))
        return list_of_time

    # Вставляет часы, принимает на вход параметр с именем столбца
    def insert_values(self, stolb_numb: str):
        self.worksheet.update(f'{stolb_numb}1:{stolb_numb}{self.last_int_in_sheets}',
                              [[hour] if hour != '00:00' else [''] for hour in self.hours_list])

    def print_values(self, stolb_numb: str):
        print(f'{stolb_numb}1:{stolb_numb}{self.last_int_in_sheets}',
              [[hour] if hour != '00:00' else [''] for hour in self.hours_list])


# Функция для перевода секунд в часы:минуты
def format_seconds(seconds):
    hours = seconds // (60 * 60)
    seconds %= (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i" % (hours, minutes)


ch_c = Changer(link_spec, [2, 10])
ch_b = Changer(link_barrister, [0, 8])

while True:
    try:
        ch_c.insert_values('K')
        ch_b.insert_values('I')
        time.sleep(3600)
    except Exception as ex:
        print(ex)
        continue

