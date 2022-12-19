import json
import os
import re

import PySimpleGUI as sg
import pdfkit
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from webdriver_manager.firefox import DriverManager

class QCBL:
    BASE_URL = 'http://10.132.246.246'

    def __init__(self):
        self.password = None
        self.username = None
        self.stu_id = None
        self.options_pdf = None
        self.path = None
        self.print_type = 'print_exp/'
        self.driver = webdriver.Firefox(DriverManager(cache_valid_range=7).install())
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
            self.wait.until(method=ec.title_contains("匿名用户"), message="超时啦")
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

    def print_report(self, url, locate, output):
        output = os.path.join(locate, output + '.pdf')
        print(output)
        self.options_pdf['footer-left'] = url
        pdfkit.from_url(url, output, options=self.options_pdf)

    def print_by_problem_id(self, problem_id, path, method="course", course_id=0):
        if method == 'course':
            problem_url = f'{self.BASE_URL}/judge/course/{course_id}/judgelist/' \
                          f'?problem={problem_id}&userprofile={self.stu_id}'
            self.driver.get(problem_url)
            self.wait.until(ec.presence_of_element_located(
                (By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table')), message="超时啦")
            report_url = self.driver.find_element(
                By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[1]/td[1]/a'
            ).get_attribute('href') + self.print_type
        elif method == 'id':
            problem_url = f'{self.BASE_URL}/judge/judgelist/?problem={problem_id}&userprofile={self.stu_id}'
            self.driver.get(problem_url)
            self.wait.until(ec.presence_of_element_located((By.ID, 'problemStatus')), message="超时啦")
            report_url = self.driver.find_element(
                By.XPATH, '//*[@id="problemStatus"]/table/tbody/tr/td[1]/a'
            ).get_attribute('href') + self.print_type
        else:
            return
        self.driver.get(report_url)
        self.wait.until(ec.title_contains('判题编号'), message="超时啦")
        output_list = self.driver.title.split(':')
        output = output_list[0] + '_' + output_list[1]
        self.print_report(report_url, path, output)

    def by_problem_id(self, problem_list):
        for i in problem_list:
            self.print_by_problem_id(i, self.path, "id")

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
            os.makedirs(os.path.join(self.path, dictionary_volume[t][1]), exist_ok=True)
            print_path = os.path.join(self.path, dictionary_volume[t][1])
            volume_url = dictionary_volume[t][0]
            self.driver.get(volume_url)
            self.wait.until(ec.presence_of_all_elements_located((By.ID, 'problemStatus')), message="超时啦")
            problems = []
            rows = [tmp_p for tmp_p in self.driver.find_elements(By.CSS_SELECTOR, '.table>tbody>tr') if tmp_p.text]
            for i in range(0, len(rows)):
                problems.append(self.driver.find_element(
                    By.XPATH, f'//*[@id="problemStatus"]/table/tbody/tr[{i + 1}]/td[2]').text)
            for problem_id in problems:
                self.print_by_problem_id(problem_id, print_path, "course", course_id)
