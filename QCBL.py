import json
import os
import re
from concurrent.futures import ThreadPoolExecutor

import PySimpleGUI as sg
import pdfkit
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class QCBL:
    BASE_URL = 'http://10.132.246.246'

    def __init__(self):
        self.password = None
        self.username = None
        self.stu_id = None
        self.options_pdf = None
        self.print_path = None
        self.print_type = 'print_exp/'
        self.driver = webdriver.Edge(EdgeChromiumDriverManager(cache_valid_range=7).install())
        self.wait = WebDriverWait(self.driver, 3, 0.5)

    def __del__(self):
        self.driver.quit()

    def get_default_user(self):
        with open("user.json", "r") as f:
            user = json.load(f)  # 加载学号和密码
            self.username = user["username"]
            self.password = user["password"]

    def set_default_user(self):
        with open("user.json", "w") as f:
            user = {"username": self.username, "password": self.password}
            json.dump(user, f)

    def login(self, username, password):
        self.username = username
        self.password = password
        try:
            self.driver.get(self.BASE_URL)
            self.wait.until(method=ec.title_contains("匿名用户"))
            self.driver.find_element(By.NAME, "username").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//form[@class='navbar-form pull-right']").submit()
            self.wait.until_not(method=ec.title_contains("匿名用户"), message="用户名或者密码不对,登录失败")
        except exceptions.TimeoutException as e:
            raise TimeoutError(e.msg)
        else:
            self.set_options_pdfkit(self.driver.get_cookies())

    def set_options_pdfkit(self, cookies):
        self.options_pdf = {
            'page-size': 'A4',
            'header-right': '[title]',
            'footer-right': '[page]',
            'cookie': [
                (cookies[0]['name'], cookies[0]['value']),
                (cookies[1]['name'], cookies[1]['value'])
            ],
        }

    def get_stu_id(self):
        self.driver.find_elements(By.CLASS_NAME, 'navbar-link')[0].get_attribute('href')
        self.stu_id = self.driver.title.split("/")[2]
        print("当前用户的ID属性值为：", self.stu_id)

    def print_by_problem_id(self, problem_url, path, method):
        # TO BE verified: 将selenium修改为request
        response = requests.get(problem_url, cookies=self.options_pdf['cookie'])
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='table table-hover').find('tbody')
        rows = table.find_all('tr')
        report_url = None
        for row in rows:
            columns = row.find_all('td')
            if columns[5].text.strip() == '答案正确':
                report_url = f"{columns[0].find('a').get('href')}{self.print_type}"
                break
        # self.driver.get(problem_url)
        # if method == 'course':
        #     self.wait.until(ec.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table')))
        #     report_url = self.driver.find_element(
        #         By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[1]/td[1]/a'
        #     ).get_attribute('href') + self.print_type
        # elif method == 'id':
        #     self.wait.until(ec.presence_of_element_located((By.ID, 'problemStatus')))
        #     report_url = self.driver.find_element(
        #         By.XPATH, '//*[@id="problemStatus"]/table/tbody/tr/td[1]/a'
        #     ).get_attribute('href') + self.print_type
        # else:
        #     return
        if report_url is None:
            return
        self.driver.get(report_url)
        self.wait.until(ec.title_contains('判题编号'))
        # 注意验证！
        # outputs = self.driver.title.split(':')
        outputs = response.text.title().split(':')
        output_path = os.path.join(path, f'{outputs[0]}_{outputs[1]}.pdf')
        self.options_pdf['footer-left'] = report_url
        pdfkit.from_url(report_url, output_path, options=self.options_pdf)
        return output_path

    def by_problem_id(self, problem_list):
        with ThreadPoolExecutor(len(problem_list)) as executor:
            with tqdm(total=len(problem_list), desc=self.print_type.split('/')[0]) as pbar:
                args = [{
                    'problem_url': f'{self.BASE_URL}/judge/judgelist/?problem={problem_id}&userprofile={self.stu_id}',
                    'path': self.print_path,
                    'method': 'id'
                } for problem_id in problem_list]
                for result in executor.map(self.print_by_problem_id, args):
                    print(result)
                    pbar.update()
        # for i in problem_list:
        #     self.print_by_problem_id(i, self.print_path, "id")

    def by_volume(self, course_id):
        course_url = f'{self.BASE_URL}/course/{course_id}/detail/'
        self.driver.get(course_url)
        datalist_volume = []
        dictionary_volume = {}
        vo = 0
        rows = [volume for volume in self.driver.find_elements(By.CSS_SELECTOR, 'tbody>tr') if volume.text]
        for row in rows:
            # TODO 修改卷数的遍历
            datalist_volume.append([volume.text for volume in row.find_elements(By.CSS_SELECTOR, 'td') if volume.text])
            vo += 1
            dictionary_volume.update({
                int(re.findall(r"\d+\.?\d*", datalist_volume[vo - 1][0])[0]):
                    [self.driver.find_element(
                        By.XPATH, f'/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[{vo}]/td[2]/a'
                    ).get_attribute('href'), datalist_volume[vo - 1][1]]
            })
        while True:
            tmp = sg.popup_get_text(
                message='请输入要打印的卷数：\n连续的用"-"(例588-598),分散的用"."(例588.589)',
                font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True, size=(30, 1)
            )
            if sum(1 for i in tmp if '-' in i) != 1:
                volume_list = list(map(int, tmp.split('.')))
                if sum(1 for i in volume_list if i not in dictionary_volume) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True)
                else:
                    break
            else:
                begin, end = list(map(int, tmp.split('-')))
                if end < begin or sum(1 for i in range(begin, end + 1) if i not in dictionary_volume) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico', keep_on_top=True)
                else:
                    volume_list = [i for i in range(begin, end + 1)]
                    break
        print(f'选定的卷数:{volume_list}')
        for t in volume_list:
            os.makedirs(os.path.join(self.print_path, dictionary_volume[t][1]), exist_ok=True)
            print_path = os.path.join(self.print_path, dictionary_volume[t][1])
            volume_url = dictionary_volume[t][0]
            self.driver.get(volume_url)
            self.wait.until(ec.presence_of_all_elements_located((By.ID, 'problemStatus')))
            problem_list = []
            rows = [tmp_p for tmp_p in self.driver.find_elements(By.CSS_SELECTOR, '.table>tbody>tr') if tmp_p.text]
            for i in range(0, len(rows)):
                problem_list.append(self.driver.find_element(
                    By.XPATH, f'//*[@id="problemStatus"]/table/tbody/tr[{i + 1}]/td[2]').text)
            with ThreadPoolExecutor(len(problem_list)) as executor:
                with tqdm(total=len(problem_list), desc=self.print_type.split('/')[0]) as pbar:
                    args = [{
                        'problem_url': f'{self.BASE_URL}/judge/course/{course_id}/judgelist/'
                                       f'?problem={problem_id}&userprofile={self.stu_id}',
                        'path': print_path,
                        'method': 'course'
                    } for problem_id in problem_list]
                    for result in executor.map(self.print_by_problem_id, args):
                        print(result)
                        pbar.update()
            # for problem_id in problem_list:
            #     self.print_by_problem_id(problem_id, print_path, "course", course_id)
