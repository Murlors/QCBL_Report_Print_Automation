import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import pdfkit
import requests
from bs4 import BeautifulSoup


class QCBL:
    BASE_URL = 'http://10.132.246.246'

    def __init__(self):
        self.window = None
        self.cookies = None
        self.password = None
        self.username = None
        self.stu_id = None
        self.options_pdf = None
        self.print_path = None
        self.print_type = 'print_exp/'
        self.is_login = False

    def get_default_user(self):
        with open("user.json", "r") as f:
            user = json.load(f)  # 加载学号和密码
            self.username = user["username"]
            self.password = user["password"]

    def get_stu_id(self):
        response = requests.get(f'{self.BASE_URL}', cookies=self.cookies)
        self.stu_id = int(re.findall(r'<a href="/user/(\d+)/detail/" class="navbar-link">.*</a>', response.text)[0]) + 4
        print("当前用户的ID属性值为：", self.stu_id)

    def set_default_user(self):
        with open("user.json", "w") as f:
            user = {"username": self.username, "password": self.password}
            json.dump(user, f, indent=4)

    def set_sg_window(self, window):
        self.window = window

    def set_options_pdfkit(self, cookies):
        self.options_pdf = {
            'page-size': 'A4',
            'header-right': '[title]',
            'footer-right': '[page]',
            'cookie': [
                ('csrftoken', cookies['csrftoken']),
                ('sessionid', cookies['sessionid'])
            ],
        }

    def login(self, username, password):
        # TO BE verified:
        self.username = username
        self.password = password
        response = requests.get(self.BASE_URL, timeout=4)
        cookies = response.cookies.get_dict()
        data = {
            'csrfmiddlewaretoken': cookies['csrftoken'],
            'username': username,
            'password': password
        }
        response = requests.post(f'{self.BASE_URL}/user/logincheck/', data=data, cookies=cookies, timeout=4)
        self.cookies = response.cookies.get_dict()
        Thread(target=self.set_options_pdfkit, args=cookies).start()
        Thread(target=self.get_stu_id).start()
        Thread(target=self.set_default_user).start()
        if self.cookies is not None and 'sessionid' in self.cookies:
            self.window.write_event_value('_login_success_', True)

    def print_by_problem_id(self, problem_url, path):
        # TO BE verified: 将selenium修改为request
        response = requests.get(problem_url, cookies=self.cookies)

        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='table table-hover').find('tbody')
        rows = table.find_all('tr')
        judges = [row.find_all('td') for row in rows]
        report_url = [f"{columns[0].find('a').get('href')}{self.print_type}"
                      for columns in judges if columns[5].text.strip() == '答案正确'][0]
        if report_url is None:
            return
        response = requests.get(report_url, cookies=self.cookies)

        output = re.findall(r"<title>(.*?)</title>", response.text)[0].replace(':', '_').strip()
        output_path = os.path.join(path, f'{output}.pdf')
        self.options_pdf['footer-left'] = report_url
        pdfkit.from_url(report_url, output_path, options=self.options_pdf)
        return output_path

    def by_problem_id(self, problem_list, course_id=-1):
        with ThreadPoolExecutor(len(problem_list)) as executor:
            progress = 0
            self.window.write_event_value(
                '_print_progress_', {'progress': progress, 'len_of_problem': len(problem_list), 'result': None})

            args = [{
                'problem_url':
                    f'{self.BASE_URL}/judge/'
                    f'course/{course_id}/' if course_id != -1 else ''
                    f'judgelist/?problem={problem_id}&userprofile={self.stu_id}',
                'path': self.print_path
            } for problem_id in problem_list]

            for result in executor.map(self.print_by_problem_id, args):
                progress += 1
                self.window.write_event_value(
                    '_print_progress_', {'progress': progress, 'len_of_problem': len(problem_list), 'result': result})

        self.window.write_event_value('_print_success_', True)

    def by_volume(self, course_id):
        course_url = f'{self.BASE_URL}/course/{course_id}/detail/'
        # TO BE verified: 将selenium修改为request
        response = requests.get(course_url, cookies=self.cookies)

        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='table table-hover').find('tbody')
        rows = table.find_all('tr')
        volumes = [row.find_all('td') for row in rows]
        volume_dict = {int(re.findall(r"\d+\.?\d*", volume[0])[0]):
                           {'text': volume[1].text,
                            'href': volume[1].find('a').get('href')}
                       for volume in volumes}

        input_volume = self.get_input_volume(volume_dict)

        for volume in input_volume:
            print_path = os.path.join(self.print_path, volume_dict[volume]['text'])
            os.makedirs(print_path, exist_ok=True)

            volume_url = volume_dict[volume]['href']
            response = requests.get(volume_url, cookies=self.cookies)

            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find('table', class_='table table-hover').find('tbody')
            rows = table.find_all('tr')
            problems = [row.find_all('td') for row in rows]
            problem_list = [int(re.findall(r"\d+\.?\d*", problem[1])[0]) for problem in problems]

            self.by_problem_id(problem_list, course_id)

    def get_input_volume(self, volume_dict):
        self.window.write_event_value('_get_input_volume_', volume_dict)

        while True:
            event, values = self.window.read()

            if event == '_input_volume_':
                input_volume = values[event]
                print(f'选定的卷数:{input_volume}')
                return input_volume
