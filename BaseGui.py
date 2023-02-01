import os
from threading import Thread

import PySimpleGUI as sg

from QCBL import QCBL


class BaseGUI:
    icon = 'data:image/x-icon;base64,AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAD///8A////AP///wD///8H////Rv///5n////S////8P////z///////////////////////////////////////////////////////////////////////////////z////w////0v///5n///9G////B////wD///8A////AP///wD///8A////If///53////v/////////////////////////////////////////////////////////////////////////////////////////////////////////////////f39//Hx8e////+d////If///wD///8A////AP///yH////B/v7+//z8/P/8/Pz//Pz8//z8/P/8/Pz//Pz8//z8/P/8/Pz//Pz8//z8/P/8/Pz//Pz8//39/f/////////////////////////////////9/f3//Pz8//39/f/s7Oz/a2tr/66urv/7+/vB////If///wD///8H////nff39/+Hh4f/YmJi/2RkZP9kZGT/ZGRk/2RkZP9kZGT/ZGRk/2RkZP9kZGT/ZGRk/2RkZP9kZGT/ZmZm/3Nzc/+Tk5P/xsbG//T09P//////9fX1/4ODg/9iYmL/ZGRk/2RkZP8yMjL/EBAQ/7Kysv////+d////B////0b////v/Pz8/87Ozv+9vb3/vr6+/76+vv++vr7/wMDA/7+/v/++vr7/vr6+/76+vv++vr7/vr6+/76+vv+7u7v/qamp/4ODg/9YWFj/WFhY/6ioqP/y8vL/zs7O/729vf+/v7//tra2/0RERP9PT0//3Nzc/////+////9G////mf/////////////////////////////////////u7u7/8fHx//////////////////////////////////////////////////X19f+9vb3/Xl5e/2RkZP/f39/////////////39/f/sbGx/+3t7f///////////////5n////S////////////////////////////////2NjY/1dXV//BwcH///////////////////////f39//f39//3t7e//X19f/////////////////19fX/kZGR/05OTv/R0dH/////////////////////////////////////0v////H//////////////////////////+bm5v9UVFT/nJyc//z8/P//////////////////////k5OT/0RERP9GRkb/iIiI////////////////////////////pKSk/09PT//f39/////////////////////////////////x/////f/////////////////////8/Pz/dHR0/4ODg//+/v7//////+np6f+UlJT/tra2/4uLi/9ERET/ycnJ/9DQ0P9FRUb/hYWF/7e3t/+Tk5P/5OTk////////////jIyM/2pqav/5+fn///////////////////////////3//////////////////////////7+/v/9TU1P/7e3t///////r6+v/ZmZm/15eXv9aWlr/gICA/9LS0v///////////9fX1/+FhYX/Wlpa/2BgYP9fX1//5ubm///////y8vL/V1dX/7OztP/////////////////////////////////////////////////9/f3/ampq/6Wlpf///////////7q6uv9KSkr/8fHx//v7+//9/f3/0dHR/5+fn/+dnZ3/zc3N//z8/P/7+/v/9fX1/1BQUP+urq7///////////+vr6//YWFh//n5+f///////////////////////////////////////////97e3v9RUVH/5ubm////////////2dnZ/0pKSv/o6Oj/9PT0/35+fv9QUFD/e3t7/319ff9SUlL/d3d3//Dw8P/u7u7/TExM/9DQ0P///////////+3t7f9SUlL/1dXV////////////////////////////////////////////s7Oz/2lpaf/+/v7///////////+bm5v/bm5u//z8/P+Hh4f/aGho/+np6f///////////+3t7f9wcHD/fX19//39/f93d3f/kJCQ/////////////////3Fxcf+np6f///////////////////////////////////////////+Tk5P/h4eH///////8/Pz/jY2N/0VFRf/ExMT/4+Pj/09PT//f39///////////////////////+fn5v9PT0//29vb/83Nzf9HR0b/hISE//n5+f//////kpKS/4iIiP///////////////////////////////////////////4aGhv+Wlpb///////T09P9QUFD/w8PD///////AwMD/YWFh//z8/P///////////////////////////2lpaf+1tbX//////8zMzP9MTEz/7u7u//////+ioqL/enp6////////////////////////////////////////////iIiI/5OTk///////9fX1/1FRUf+Xl5f/+fn5/8jIyP9bW1v/+Pj4///////////////////////8/Pz/YmJi/729vf/7+/v/oKCg/0tLS//w8PD//////5+fn/99fX3///////////////////////////////////////////+cnJz/fn5+///////+/v7/wMDA/0xMTP+kpKT/8fHx/1NTU//CwsL//////////////////////8vLy/9PT0//6+vr/6+vr/9ISEj/urq6//39/f//////iYmJ/5CQkP///////////////////////////////////////////8HBwf9eXl7/+fn5////////////vLy8/1paWv/29vb/sbGx/0xMTP+5ubn/7+/v//Dw8P+/v7//T09P/6enp//6+vr/YWFh/7Gxsf////////////39/f9mZmb/tbW1////////////////////////////////////////////6+vr/1FRUf/W1tb////////////T09P/TExM/+vr6///////t7e3/1paWv9TU1P/VFRU/1dXV/+wsLD///////Hx8f9PT0//ysrK////////////4ODg/1BQUP/j4+P/////////////////////////////////////////////////goKC/4eHh////////////7+/v/9FRUX/1dXV/9bW1v/w8PD/+Pj4/9vb2//Z2dn/9vb2//Ly8v/V1dX/2tra/0hISP+0tLT///////////+UlJT/d3d3///////////////////////////////////////////////////////a2tr/TExM/9TU1P//////+/v7/5SUlP9AQED/S0tL/1RUVP+Xl5f/+/v7//7+/v+enp7/VlZW/0tLS/9AQED/i4uL//n5+f//////3t7e/01NTf/R0dH///////////////////////////////////////////////////////////+bm5v/XV1d/+/v7///////+/v7/9LS0v/p6en/yMjI/0xMTP+UlJT/nJyc/0dHR//Dw8P/6urq/9HR0f/5+fn///////T09P9nZ2f/kJCR//////////////////////////////////////////////////////////////////n5+f94eHj/a2tr/+3t7f//////////////////////vr6+/2RkZP9jY2P/tra2///////////////////////y8vL/dXV1/3BwcP/29vb//////////////////////////////////////f////////////////////////////////T09P96enr/Wlpa/83Nzf///////////6+vr/97e3v/enp6/3p6ev97e3v/qamp//7+/v//////1NTU/2JiYv90dHT/8PDw//////////////////////////////////////3////x//////////////////////////////////////r6+v+ioqL/TU1N/3x8fP+2trb/RUVF/5GRkf+jo6P/o6Oj/5WVlf9DQ0P/tLS0/4KCgv9OTk7/nJyc//j4+P//////////////////////////////////////////8f///9L////////////////////////////////////////////////h4eH/kJCQ/01NTf83Nzf/3d3d/4WFhf+0tLT/9fX1/z4+Pv9JSUn/jIyM/97e3v/////////////////////////////////////////////////////S////mf//////////////////////////////////////////////////////////3d3d/1JSUv+fn5//XV1d/0pKSv+4uLj/VFRU/9XV1f///////////////////////////////////////////////////////////////5n///9G////7//////////////////////////////////////////////////////n5+f/VFRU/+Dg4P/+/v7/v7+//7CwsP9XV1f/39/f///////////////////////////////////////////////////////////v////Rv///wf///+d/////////////////////////////////////////////////////+3t7f9LS0v/eHh4/4eHh/+IiIj/fHx8/0dHR//m5ub//////////////////////////////////////////////////////////53///8H////AP///yH////B/////////////////////////////////////////////////v7+/8TExP+VlZX/lZWV/5WVlf+VlZX/v7+///39/f/////////////////////////////////////////////////////B////If///wD///8A////AP///yH///+d////7//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////v////nf///yH///8A////AP///wD///8A////AP///wf///9G////mf///9L////w/////P///////////////////////////////////////////////////////////////////////////////P////D////S////mf///0b///8H////AP///wD///8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='

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

        self.window = sg.Window(layout=self.layout, title='开摆', icon=self.icon)
        self.qcbl.set_sg_window(self.window)

        self.is_set_print_path = False

    def login(self, username, password):
        try:
            Thread(target=self.qcbl.login, args=(username, password,)).start()
        except TimeoutError as e:
            sg.popup_error("%s" % e, font=self.font_minor, icon=self.icon)

    def set_print_path(self):
        self.qcbl.print_path = sg.popup_get_folder(
            message='选择实验报告打印的位置:', default_path=os.path.join(os.getcwd(), 'print'),
            font=self.font_minor, icon=self.icon, size=(30, 1), modal=False
        )
        self.is_set_print_path = True

    def set_print_type(self):
        print_type = sg.popup_get_text(
            message='选择要打印的类型:\n1、生成实验报告\n2、生成作业\n',
            font=self.font_minor, icon=self.icon, size=(30, 1)
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
                font=self.font_minor, icon=self.icon, size=(30, 1)
            )
            if sum(1 for i in problem_id if '-' in i) != 1:
                problem_list = list(map(int, problem_id.split('.')))
                break
            else:
                begin, end = list(map(int, problem_id.split('-')))
                if end < begin:
                    sg.popup_error(
                        "题目编号编写错误！", font=self.font_minor, icon=self.icon
                    )
                else:
                    problem_list = [i for i in range(begin, end + 1)]
                    break
        return problem_list

    def get_course_id(self):
        course_id = sg.popup_get_text(
            message='1、数据结构(2021-2022-2)\n2、程序设计课程设计(2021-2022-2)\n'
                    '如果要其他课程直接输入课程编号\n速速选一个:',
            font=self.font_minor, icon=self.icon, size=(30, 1)
        )
        if course_id == '1':
            course_id = '108'
        elif course_id == '2':
            course_id = '107'
        return course_id

    def get_input_volume(self, volume_dict):
        input_volume = sg.popup_get_text(
            message='请输入要打印的卷数：\n连续的用"-"(例588-598),分散的用"."(例588.589)',
            font=("微软雅黑", 12), icon=self.icon, size=(30, 1)
        )
        if sum(1 for i in input_volume if '-' in i) != 1:
            input_volume = list(map(int, input_volume.split('.')))
            if sum(1 for i in input_volume if i not in volume_dict) >= 1:
                sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon=self.icon)
                input_volume = None
                self.window.write_event_value('_input_volume_', volume_dict)
        else:
            begin, end = list(map(int, input_volume.split('-')))
            if end < begin or sum(1 for i in range(begin, end + 1) if i not in volume_dict) >= 1:
                sg.popup_error("卷数编号填写错误！", font=("微软雅黑", 12), icon=self.icon)
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
            sg.popup_error("%s" % e, font=self.font_minor, icon=self.icon)

    def by_volume_id(self):
        course_id = self.get_course_id()
        print(f'选定的课程编号:{course_id}')

        try:
            Thread(target=self.qcbl.by_volume, args=(course_id,)).start()
        except Exception as e:
            sg.popup_error("%s" % e, font=self.font_minor, icon=self.icon)

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
                sg.popup('打印成功啦,可以退出了(也可以继续打印)', font=self.font_minor, icon=self.icon)

            if event == sg.WIN_CLOSED or event == '_exit_':
                break

        self.window.close()


if __name__ == '__main__':
    table_gui = BaseGUI()
    table_gui.run()
