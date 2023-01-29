import os
from threading import Thread

import PySimpleGUI as sg

from QCBL import QCBL


class BaseGUI:
    def __init__(self):
        self.qcbl = QCBL()
        self.qcbl.get_default_user()

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
                       [sg.Output(size=(40, 5), font=self.font_minor, background_color='light gray')]
                       ]

        self.window = sg.Window(layout=self.layout, title='开摆', icon='icon.ico')
        self.qcbl.set_sg_window(self.window)

        self.is_set_print_path = False

    def login(self, username, password):
        try:
            Thread(target=self.qcbl.login, args=(username, password,)).start()
        except TimeoutError as e:
            sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico')

    def set_print_path(self):
        self.qcbl.print_path = sg.popup_get_folder(
            message='选择实验报告打印的位置:', default_path=os.path.join(os.getcwd(), 'print'),
            font=self.font_minor, icon='icon.ico', size=(30, 1), modal=False
        )
        self.is_set_print_path = True

    def set_print_type(self):
        print_type = sg.popup_get_text(
            message='选择要打印的类型:\n1、生成实验报告\n2、生成作业\n',
            font=self.font_minor, icon='icon.ico', size=(30, 1)
        )
        if print_type.isdigit():
            if print_type == '1':
                self.qcbl.print_type = 'print_exp/'
            elif print_type == '2':
                self.qcbl.print_type = 'print_ass/'

    def get_problem_id(self):
        while True:
            problem_id = sg.popup_get_text(
                message='请输入要打印的题目编号:\n连续的用"-"(例588-598),分散的用"."(例588.589)',
                font=self.font_minor, icon='icon.ico', size=(30, 1)
            )
            if sum(1 for i in problem_id if '-' in i) != 1:
                problem_list = list(map(int, problem_id.split('.')))
                break
            else:
                begin, end = list(map(int, problem_id.split('-')))
                if end < begin:
                    sg.popup_error(
                        "题目编号编写错误！", font=self.font_minor, icon='icon.ico'
                    )
                else:
                    problem_list = [i for i in range(begin, end + 1)]
                    break
        return problem_list

    def get_course_id(self):
        course_id = sg.popup_get_text(
            message='1、数据结构(2021-2022-2)\n2、程序设计课程设计(2021-2022-2)\n'
                    '如果要其他课程直接输入课程编号\n速速选一个:',
            font=self.font_minor, icon='icon.ico', size=(30, 1)
        )
        if course_id == '1':
            course_id = '108'
        elif course_id == '2':
            course_id = '107'
        return course_id

    def get_input_volume(self, volume_dict):
        input_volume = sg.popup_get_text(
            message='请输入要打印的卷数：\n连续的用"-"(例588-598),分散的用"."(例588.589)',
            font=("微软雅黑", 12), icon='icon.ico', size=(30, 1)
        )
        if sum(1 for i in input_volume if '-' in i) != 1:
            input_volume = list(map(int, input_volume.split('.')))
            if sum(1 for i in input_volume if i not in volume_dict) >= 1:
                sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico')
                input_volume = None
                self.window.write_event_value('_input_volume_', volume_dict)
        else:
            begin, end = list(map(int, input_volume.split('-')))
            if end < begin or sum(1 for i in range(begin, end + 1) if i not in volume_dict) >= 1:
                sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon='icon.ico')
                input_volume = None
                self.window.write_event_value('_input_volume_', volume_dict)
            else:
                input_volume = [i for i in range(begin, end + 1)]

        if input_volume:
            self.window.write_event_value('_input_volume_', input_volume)

    def by_problem_id(self):
        problem_list = self.get_problem_id()
        print(f'选定的题目编号:{problem_list}')

        try:
            Thread(target=self.qcbl.by_problem_id, args=(problem_list,)).start()
        except Exception as e:
            sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico')

    def by_volume_id(self):
        course_id = self.get_course_id()
        print(f'选定的课程编号:{course_id}')

        try:
            Thread(target=self.qcbl.by_volume, args=(course_id,)).start()
        except Exception as e:
            sg.popup_error("%s" % e, font=self.font_minor, icon='icon.ico')

    def run(self):
        while True:
            event, values = self.window.read()
            if event == '_submit_':
                if not self.qcbl.is_login:
                    username = values['_username_']
                    password = values['_password_']
                    self.login(username, password)

            if event == '_login_success_':
                if not self.is_set_print_path:
                    self.set_print_path()
                self.set_print_type()
                print_by_problem_id = values[0]  # 是否根据题号打印
                if print_by_problem_id:
                    self.by_problem_id()
                else:
                    self.by_volume_id()

            if event == '_get_input_volume_':
                volume_dict = values[event]
                try:
                    self.get_input_volume(volume_dict)
                except Exception as e:
                    print(e)

            if event == '_print_progress_':
                value = values[event]
                sg.one_line_progress_meter('正在打印', value['progress'], value['len_of_problem'],
                                           self.qcbl.print_type.split('/')[0],
                                           f'打印完成:{value["result"]}' if value['result'] else '')

            if event == '_print_success_':
                sg.popup('打印成功啦,可以退出了(也可以继续打印)', font=self.font_minor, icon='icon.ico')

            if event == sg.WIN_CLOSED or event == '_exit_':
                break

        self.window.close()


if __name__ == '__main__':
    table_gui = BaseGUI()
    table_gui.run()
