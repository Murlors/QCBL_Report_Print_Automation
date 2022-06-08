import os.path
import re

import PySimpleGUI as sg
import pdfkit
import selenium.common.exceptions as exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Qcbl:
    def __init__(self):
        self.password = None
        self.username = None
        self.stu_id = None
        self.cookies = None
        self.options_pdf = None
        self.config_pdf = None
        self.path = None
        self.driver = webdriver.Ie()
        self.wait = WebDriverWait(self.driver, 3.6, 0.25)

    def __del__(self):
        self.driver.quit()

    def login(self, username, password):
        self.username = username
        self.password = password
        try:
            self.driver.get("http://10.132.246.246/")
            self.wait.until(method=EC.title_contains("匿名用户"), message="超时啦")
            self.driver.find_element(By.NAME, "username").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.XPATH, "//form[@class='navbar-form pull-right']").submit()
            self.wait.until_not(method=EC.title_contains("匿名用户"), message="用户名或者密码不对，登录失败")
        except exceptions.TimeoutException as e:
            raise TimeoutError(e.msg)
        else:
            self.cookies = self.driver.get_cookies()
            self.get_options_pdfkit()

    def get_stu_id(self):
        element = self.driver.find_element(By.PARTIAL_LINK_TEXT, "%s" % self.username)
        self.driver.execute_script("arguments[0].click();", element)
        self.wait.until(method=EC.title_contains("用户信息"), message="超时啦")
        title = self.driver.title.split(" ")
        self.stu_id = str(int(title[2]) - 4)
        print("当前用户的ID属性值为：", self.stu_id)

    def get_options_pdfkit(self):
        self.options_pdf = {
            'page-size': 'A4',
            'header-right': '[title]',
            'footer-right': '[page]',
            'cookie': [
                (self.cookies[0]['name'], self.cookies[0]['value']),
                (self.cookies[1]['name'], self.cookies[1]['value'])
            ],
        }

    def report_print(self, url, locate, output):
        output = os.path.join(locate, output + '.pdf')
        print(output)
        self.options_pdf['footer-left'] = url
        pdfkit.from_url(url, output, options=self.options_pdf)

    def print_by_problem_id(self, problem_id, locate, method="course", course_id=0):
        if method == "course":
            problem_url = "http://10.132.246.246/judge/course/" + str(course_id) + "/judgelist/?problem=" + \
                          str(problem_id) + "&userprofile=" + self.stu_id
            self.driver.get(problem_url)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table')),
                            message="超时啦")
            report_url = self.driver.find_element(
                By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[1]/td[1]/a'). \
                get_attribute('href') + 'print_exp/'
        elif method == "id":
            problem_url = "http://10.132.246.246/judge/judgelist/?problem=" \
                          + str(problem_id) + "&userprofile=" + self.stu_id
            self.driver.get(problem_url)
            self.wait.until(EC.presence_of_element_located((By.ID, 'problemStatus')), message="超时啦")
            report_url = self.driver.find_element(
                By.XPATH, '//*[@id="problemStatus"]/table/tbody/tr/td[1]/a').get_attribute('href') + 'print_exp/'

        self.driver.get(report_url)
        self.wait.until(EC.title_contains('判题编号'), message="超时啦")
        output_list = self.driver.title.split(':')
        output = output_list[0] + '_' + output_list[1]
        self.report_print(report_url, locate, output)

    def by_problem_id(self, problem_list):
        for i in problem_list:
            self.print_by_problem_id(i, self.path, "id")

    def by_volume(self, course_id):
        course_url = 'http://10.132.246.246/course/' + course_id + '/detail/'
        self.driver.get(course_url)
        datalist_volume = []
        dictionary_volume = {}
        kk = 0
        rows = [tmp_v for tmp_v in self.driver.find_elements(By.CSS_SELECTOR, 'tbody>tr') if tmp_v.text]
        for row in rows:
            datalist_volume.append([tmp_v.text for tmp_v in row.find_elements(By.CSS_SELECTOR, 'td') if tmp_v.text])
            kk += 1
            dictionary_volume.update({
                int(re.findall(r"\d+\.?\d*", datalist_volume[kk - 1][0])[0]):
                    [self.driver.find_element(
                        By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/table/tbody/tr[%d]/td[2]/a' % kk).
                     get_attribute('href'), datalist_volume[kk - 1][1]]
            })
        while True:
            tmp = sg.popup_get_text(message='请输入要打印的卷数：\n'
                                            '连续的用"-"(例588-598)，分散的用.(例588.589)',
                                    font=("微软雅黑", 16),
                                    icon='icon.ico',
                                    keep_on_top=True,
                                    size=(30, 1)
                                    )
            volume_list = []
            if sum(1 for i in tmp if '-' in i) != 1:
                volume_list = list(map(int, tmp.split('.')))
                if sum(1 for i in volume_list if i not in dictionary_volume) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 16), icon='icon.ico', keep_on_top=True)
                else:
                    break
            else:
                begin, end = list(map(int, tmp.split('-')))
                if end < begin or sum(1 for i in range(begin, end + 1) if i not in dictionary_volume) >= 1:
                    sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 16), icon='icon.ico', keep_on_top=True)
                else:
                    for i in range(begin, end + 1):
                        volume_list.append(i)
                    break

        print('选定的卷数:')
        print(volume_list)
        for t in volume_list:
            os.makedirs(os.path.join(self.path, dictionary_volume[t][1]), exist_ok=True)
            volume_url = dictionary_volume[t][0]
            self.driver.get(volume_url)
            datalist_problem = []
            dictionary_problem = {}
            pp = 0
            rows = [tmp_p for tmp_p in self.driver.find_elements(By.CSS_SELECTOR, 'tbody>tr') if tmp_p.text]
            for row in rows:  # 逐行获取
                datalist_problem.append(
                    [tmp_p.text for tmp_p in row.find_elements(By.CSS_SELECTOR, 'td') if tmp_p.text])
                if pp > 0:
                    dictionary_problem.update({
                        int(datalist_problem[pp][1]):
                        self.driver.find_element(
                            By.XPATH, '//*[@id="problemStatus"]/table/tbody/tr[%d]/td[3]/a' % pp).get_attribute('href')
                    })
                pp += 1
            for problem_id, problem_url in dictionary_problem.items():
                self.print_by_problem_id(problem_id, os.path.join(self.path, dictionary_volume[t][1]), "course",
                                         course_id)


class BaseGUI:
    def __init__(self):
        try:
            self.my = Qcbl()
        except exceptions.WebDriverException as e:
            sg.popup_error("浏览器启动失败,更新WebDriver的版本！\n%s" % e.msg,
                           font=("微软雅黑", 16), icon='icon.ico', keep_on_top=True)
        else:
            sg.theme('LightGrey1')
            self.font = ("微软雅黑", 16)
            self.flag = True
            self.way = None
            self.input = [[sg.Text('学号：', font=self.font),
                           sg.InputText(key='_username_', default_text=self.my.username, font=self.font, size=(16, 1))],
                          [sg.Text('密码：', font=self.font),
                           sg.InputText(key='_password_', default_text=self.my.password, password_char='*',
                                        font=self.font,
                                        size=(16, 1))]
                          ]
            self.radio = sg.Frame(layout=[
                [sg.Radio('根据题号打印', group_id="_radio_", font=("微软雅黑", 14))],
                [sg.Radio('根据课程打印', group_id="_radio_", default=True, font=("微软雅黑", 14))]],
                title='选择要打印的方式：', font=("微软雅黑", 14), relief=sg.RELIEF_SUNKEN
            )
            self.layout = [[sg.Column(self.input), self.radio],
                           [sg.Submit('提交', key='_submit_', font=("微软雅黑", 14), size=(8, 1)),
                            sg.Exit('退出', key='_exit_', font=("微软雅黑", 14), size=(8, 1))],
                           [sg.Output(size=(40, 5), font=self.font, background_color='light gray')],
                           ]
            self.window = sg.Window(
                title='开摆',
                layout=self.layout,
                keep_on_top=True,
                finalize=True,
            )
            self.run()

    def run(self):
        while True:
            event, values = self.window.read()
            if event == '_submit_':
                if self.flag:
                    username = values['_username_']
                    password = values['_password_']
                    try:
                        if username == '':
                            sg.popup_error("请输入学号！", font=self.font, icon='icon.ico', keep_on_top=True, )
                            continue
                        if password == '':
                            sg.popup_error("请输入密码！", font=self.font, icon='icon.ico', keep_on_top=True, )
                            continue
                        self.my.login(username, password)
                        self.my.get_stu_id()
                    except TimeoutError as e:
                        sg.popup_error("%s" % e, font=self.font, icon='icon.ico', keep_on_top=True, )
                        continue
                    else:
                        self.my.path = sg.popup_get_folder(message='选择实验报告打印的位置：',
                                                           default_path=os.getcwd(),
                                                           font=self.font,
                                                           icon='icon.ico',
                                                           keep_on_top=True,
                                                           size=(30, 1),
                                                           modal=False,
                                                           )
                        self.flag = False
                self.way = values[0]
                if self.way:
                    while True:
                        tmp = sg.popup_get_text(message='请输入要打印的题目编号：\n'
                                                        '连续的用"-"(例588-598)，分散的用.(例588.589)',
                                                font=self.font,
                                                icon='icon.ico',
                                                keep_on_top=True,
                                                size=(30, 1)
                                                )
                        problem_list = []
                        if sum(1 for i in tmp if '-' in i) != 1:
                            problem_list = list(map(int, tmp.split('.')))
                            break
                        else:
                            begin, end = list(map(int, tmp.split('-')))
                            if end < begin:
                                sg.popup_error("题目编号编写错误！", font=self.font, icon='icon.ico', keep_on_top=True)
                            else:
                                for i in range(begin, end + 1):
                                    problem_list.append(i)
                                break

                    print('选定的题目编号:')
                    print(problem_list)
                    try:
                        self.my.by_problem_id(problem_list)
                    except Exception as e:
                        sg.popup_error("%s" % e, font=self.font, icon='icon.ico', keep_on_top=True, )
                        continue
                elif not self.way:
                    course_id = sg.popup_get_text(message='1、数据结构(2021-2022-2)\n'
                                                          '2、程序设计课程设计(2021-2022-2)\n'
                                                          '如果要其他课程直接输入课程编号\n'
                                                          '速速选一个：',
                                                  font=self.font,
                                                  icon='icon.ico',
                                                  keep_on_top=True,
                                                  size=(30, 1)
                                                  )
                    if course_id == '1':
                        course_id = '108'
                    elif course_id == '2':
                        course_id = '107'
                    try:
                        self.my.by_volume(course_id)
                    except Exception as e:
                        sg.popup_error("%s" % e, font=self.font, icon='icon.ico', keep_on_top=True, )
                        continue
                sg.popup('打印结束啦，可以退出了(也可以继续打印)', font=self.font, icon='icon.ico', keep_on_top=True, )

            if event == sg.WIN_CLOSED or event == '_exit_':
                self.my.__del__()
                break

        self.window.close()


if __name__ == '__main__':
    table_gui = BaseGUI()
