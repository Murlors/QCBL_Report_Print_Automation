import os
import re
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

import requests
from bs4 import BeautifulSoup

from util import config, save_config, requests_handler, pdf_print_handle, fail_list_append


class QCBL:
    BASE_URL = 'http://10.132.246.246'

    def __init__(self):
        self.window = None
        self.cookies = None
        self.stu_id = None
        self.options_pdf = None
        self.print_path = None
        self.print_type = 'print_exp/'
        self.is_login = False

    def get_stu_id(self):
        response = requests_handler('GET', f'{self.BASE_URL}', cookies=self.cookies)
        self.stu_id = re.findall(r'<a href="/user/(\d+)/detail/" class="navbar-link">.*</a>', response.text)[0]
        print(f"当前用户的ID属性值为: {self.stu_id}")

    def set_sg_window(self, window):
        self.window = window

    def set_options_pdfkit(self):
        self.options_pdf = {
            'page-size': 'A4',
            'header-right': '[title]',
            'footer-right': '[page]',
            'cookie': [
                ('csrftoken', self.cookies['csrftoken']),
                ('sessionid', self.cookies['sessionid'])
            ],
        }

    def login(self, username, password):
        config.update({'username': username, 'password': password})
        session = requests.Session()
        session.get(self.BASE_URL, timeout=4)
        cookies = session.cookies.get_dict()
        data = {
            'csrfmiddlewaretoken': cookies['csrftoken'],
            'username': username,
            'password': password
        }
        session.post(f'{self.BASE_URL}/user/logincheck/', data=data, timeout=4)
        self.cookies = session.cookies.get_dict()
        if self.cookies is not None and 'sessionid' in self.cookies:
            Thread(target=self.get_stu_id).start()
            Thread(target=self.set_options_pdfkit).start()
            Thread(target=save_config).start()
            self.window.write_event_value('_login_success_', True)

    def report_print(self, problem_url, path):
        try:
            response = requests_handler('GET', problem_url, cookies=self.cookies)
        except Exception as e:
            return e

        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='table table-hover').find('tbody')
        rows = table.find_all('tr')
        report_referer_url = [self.BASE_URL + columns[0].find('a').get('href')
                              for columns in (row.find_all('td') for row in rows)
                              if columns[5].text.strip() == '答案正确'][0]

        if report_referer_url is None:
            return
        report_url = report_referer_url + self.print_type
        try:
            response = requests_handler('GET', report_url, cookies=self.cookies)
        except Exception as e:
            if '404' in str(e):
                fail_list_append(problem_url)
            return e
        output = re.findall(r"<title>(.*?)</title>", response.text)[0].replace(':', '_').replace(' ', '').strip()
        output_path = os.path.join(path, f'{output}.pdf')
        self.options_pdf['footer-left'] = report_url

        return pdf_print_handle(report_url, output_path, self.options_pdf)

    def by_problem_id(self, print_path, problem_list, course_id=-1):
        with ThreadPoolExecutor(config.get('n_threads', 2)) as executor:
            progress = 0
            self.window.write_event_value(
                '_print_progress_', {'progress': progress, 'len_of_problem': len(problem_list), 'result': None})
            problem_url_list = [
                f'{self.BASE_URL}/judge'
                f'/course/{course_id}/judgelist/?problem={problem_id}&userprofile={self.stu_id}'
                for problem_id in problem_list] if course_id != -1 else [
                f'{self.BASE_URL}/judge'
                f'/judgelist/?problem={problem_id}&userprofile={self.stu_id}'
                for problem_id in problem_list]
            for result in executor.map(self.report_print, problem_url_list,
                                       [print_path] * len(problem_list)):
                progress += 1
                self.window.write_event_value(
                    '_print_progress_', {'progress': progress, 'len_of_problem': len(problem_list), 'result': result})

    def print_by_problem_id(self, print_path, problem_list):
        self.by_problem_id(print_path, problem_list)

        self.window.write_event_value('_print_success_', True)

    def get_volume_dict(self, course_id):
        course_url = f'{self.BASE_URL}/course/{course_id}/detail/'
        response = requests_handler('GET', course_url, cookies=self.cookies)

        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='table table-hover').find('tbody')
        rows = table.find_all('tr')
        volumes = [row.find_all('td') for row in rows]
        volume_dict = {
            int(re.findall(r"\d+\.?\d*", str(volume[0]))[0]):
                {'text': volume[1].text.replace(' ', '').strip(), 'href': volume[1].find('a').get('href')}
            for volume in volumes}

        self.window.write_event_value('_get_input_volume_', {'course_id': course_id, 'volume_dict': volume_dict})

    def print_by_volume(self, course_id, volume_dict, input_volume):
        for volume in input_volume:
            print_path = os.path.join(self.print_path, volume_dict[volume]['text'])
            os.makedirs(print_path, exist_ok=True)

            volume_url = volume_dict[volume]['href']
            response = requests_handler('GET', self.BASE_URL + volume_url, cookies=self.cookies)

            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find('table', class_='table table-hover').find('tbody')
            rows = table.find_all('tr')
            problems = [row.find_all('td') for row in rows]
            problem_list = [int(re.findall(r"\d+\.?\d*", str(problem[1]))[0]) for problem in problems]

            self.by_problem_id(print_path, problem_list, course_id)

        self.window.write_event_value('_print_success_', True)
