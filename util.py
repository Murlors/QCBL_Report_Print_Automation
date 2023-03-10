import json
import os.path
import time

import pdfkit
import requests


def verbose_print(*args):
    if config.get('verbose', False):
        print(*args)


def get_config():
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)


def save_config():
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def requests_handler(method, url, **kwargs):
    for i in range(config.get('n_tries', 5)):
        try:
            if method == 'GET':
                response = requests.get(url, **kwargs)
            elif method == 'POST':
                response = requests.post(url, **kwargs)
            else:
                raise Exception('requests_handler()方法的method参数只能为GET或POST')
            if response.status_code == 200:
                return response
            else:
                raise Exception(f'请求{url}失败，状态码为{response.status_code}')
        except Exception:
            verbose_print(f'请求{url}失败，正在重试第{i + 1}次')
            time.sleep(config.get('time_between_tries', 3))

    fail_list.append(url)
    raise Exception(f"请求{url}失败")


def pdf_print_handle(report_url, output_path, options_pdf):
    for i in range(config.get('n_tries', 5)):
        try:
            pdfkit.from_url(report_url, output_path, options=options_pdf)
            return output_path
        except Exception:
            verbose_print(f'打印失败，正在重试第{i + 1}次: {report_url}')
            time.sleep(config.get('time_between_tries', 3))

    return f"打印失败{report_url}"


config = get_config()
fail_list = []
