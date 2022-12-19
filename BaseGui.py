import os

import PySimpleGUI as sg

from QCBL import QCBL


class BaseGUI:
    def __init__(self):
        self.qcbl = QCBL()
        self.qcbl.get_default_user()
        # sg.popup_error("%s" % e, font=("微软雅黑", 16), icon='icon.ico', keep_on_top=True)
        sg.theme('LightGrey1')
        self.font_main = ("微软雅黑", 16)
        self.font_minor = ("微软雅黑", 12)
        self.input = [[sg.Text('学号:', font=self.font_main),
                       sg.InputText(key='_username_', default_text=self.qcbl.username,
                                    font=self.font_main, size=(12, 1))],
                      [sg.Text('密码:', font=self.font_main),
                       sg.InputText(key='_password_', default_text=self.qcbl.password,
                                    password_char='*', font=self.font_main, size=(12, 1))]
                      ]
        self.radio = sg.Frame(layout=[
            [sg.Radio('根据题号打印', group_id="_radio_", font=self.font_minor)],
            [sg.Radio('根据课程打印', group_id="_radio_", default=True, font=self.font_minor)]],
            title='选择要打印的方式:', font=self.font_minor, relief=sg.RELIEF_SUNKEN
        )
        self.layout = [[sg.Column(self.input), self.radio],
                       [sg.Submit('提交', key='_submit_', font=self.font_minor, size=(8, 1)),
                        sg.Exit('退出', key='_exit_', font=self.font_minor, size=(8, 1))],
                       [sg.Output(size=(32, 5), font=self.font_main, background_color='light gray')]
                       ]
        self.window = sg.Window(layout=self.layout, title='开摆', icon='icon.ico', keep_on_top=True, finalize=True)
        self.run()

    def run(self):
        set_location_flag = True
        while True:
            event, values = self.window.read()
            if event == '_submit_':
                if set_location_flag:
                    username = values['_username_']
                    password = values['_password_']
                    try:
                        self.qcbl.login(username, password)
                        self.qcbl.get_stu_id()
                        self.qcbl.set_default_user()
                    except TimeoutError as e:
                        sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico', keep_on_top=True)
                        # continue
                    else:
                        self.qcbl.path = sg.popup_get_folder(
                            message='选择实验报告打印的位置:', default_path=os.path.join(os.getcwd(), 'print'),
                            font=self.font_minor, icon='icon.ico', keep_on_top=True, size=(30, 1), modal=False
                        )
                        set_location_flag = False
                print_type = sg.popup_get_text(
                    message='选择要打印的类型:\n1、生成实验报告\n2、生成作业\n',
                    font=self.font_minor, icon='icon.ico', keep_on_top=True, size=(30, 1)
                )
                if print_type.isdigit():
                    if print_type == '1':
                        self.qcbl.print_type = 'print_exp/'
                    elif print_type == '2':
                        self.qcbl.print_type = 'print_ass/'
                print_way = values[0]  # 是否根据题号打印
                if print_way:
                    while True:
                        tmp = sg.popup_get_text(
                            message='请输入要打印的题目编号:\n连续的用"-"(例588-598),分散的用"."(例588.589)',
                            font=self.font_minor, icon='icon.ico', keep_on_top=True, size=(30, 1)
                        )
                        if sum(1 for i in tmp if '-' in i) != 1:
                            problem_list = list(map(int, tmp.split('.')))
                            break
                        else:
                            begin, end = list(map(int, tmp.split('-')))
                            if end < begin:
                                sg.popup_error(
                                    "题目编号编写错误！", font=self.font_minor, icon='icon.ico', keep_on_top=True
                                )
                            else:
                                problem_list = [i for i in range(begin, end + 1)]
                                break
                    print(f'选定的题目编号:{problem_list}')
                    try:
                        self.qcbl.by_problem_id(problem_list)
                    except Exception as e:
                        sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico', keep_on_top=True)
                        continue
                else:
                    course_id = sg.popup_get_text(
                        message='1、数据结构(2021-2022-2)\n2、程序设计课程设计(2021-2022-2)\n'
                                '如果要其他课程直接输入课程编号\n速速选一个:',
                        font=self.font_minor, icon='icon.ico', keep_on_top=True, size=(30, 1)
                    )
                    if course_id == '1':
                        course_id = '108'
                    elif course_id == '2':
                        course_id = '107'
                    try:
                        self.qcbl.by_volume(course_id)
                    except Exception as e:
                        sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico', keep_on_top=True)
                        continue
                sg.popup('打印结束啦,可以退出了(也可以继续打印)', font=self.font_minor, icon='icon.ico',
                         keep_on_top=True)

            if event == sg.WIN_CLOSED or event == '_exit_':
                self.qcbl.__del__()
                break

        self.window.close()


if __name__ == '__main__':
    table_gui = BaseGUI()
