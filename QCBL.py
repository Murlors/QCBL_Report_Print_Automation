import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import PySimpleGUI as sg
import pdfkit
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class QCBL:
    BASE_URL = 'http://10.132.246.246'

    def __init__(self):
        self.cookies = None
        self.password = None
        self.username = None
        self.stu_id = None
        self.options_pdf = None
        self.print_path = None
        self.print_type = 'print_exp/'

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
            json.dump(user, f)

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
        response = requests.get(self.BASE_URL)
        cookies = response.cookies.get_dict()
        data = {
            'csrfmiddlewaretoken': cookies['csrftoken'],
            'username': username,
            'password': password
        }
        response = requests.post(f'{self.BASE_URL}/user/logincheck/', data=data, cookies=cookies)
        self.cookies = response.cookies.get_dict()
        Thread(target=self.set_options_pdfkit, args=cookies).start()
        Thread(target=self.get_stu_id).start()
        Thread(target=self.set_default_user).start()

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

    def by_problem_id(self, problem_list):
        with ThreadPoolExecutor(len(problem_list)) as executor:
            with tqdm(total=len(problem_list), desc=self.print_type.split('/')[0]) as pbar:
                args = [{
                    'problem_url': f'{self.BASE_URL}/judge/judgelist/?problem={problem_id}&userprofile={self.stu_id}',
                    'path': self.print_path
                } for problem_id in problem_list]
                for result in executor.map(self.print_by_problem_id, args):
                    print(result)
                    pbar.update()

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

        input_volume = self.get_input(volume_dict)

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
            with ThreadPoolExecutor(len(problem_list)) as executor:
                with tqdm(total=len(problem_list), desc=self.print_type.split('/')[0]) as pbar:
                    args = [{
                        'problem_url': f'{self.BASE_URL}/judge/course/{course_id}/judgelist/'
                                       f'?problem={problem_id}&userprofile={self.stu_id}',
                        'path': print_path
                    } for problem_id in problem_list]
                    for result in executor.map(self.print_by_problem_id, args):
                        print(result)
                        pbar.update()

    @staticmethod
    def get_input(volume_dict):
        while True:
            input_v = sg.popup_get_text(
                message='请输入要打印的卷数：\n连续的用"-"(例588-598),分散的用"."(例588.589)',
                font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True, size=(30, 1)
            )
            if sum(1 for i in input_v if '-' in i) != 1:
                input_volume = list(map(int, input_v.split('.')))
                if sum(1 for i in input_volume if i not in volume_dict) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True)
                else:
                    break
            else:
                begin, end = list(map(int, input_v.split('-')))
                if end < begin or sum(1 for i in range(begin, end + 1) if i not in volume_dict) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True)
                else:
                    input_volume = [i for i in range(begin, end + 1)]
                    break
        print(f'选定的卷数:{input_volume}')
        return input_volume
