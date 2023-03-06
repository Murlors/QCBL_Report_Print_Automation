# 千锤百炼实验报告自动化打印

## QCBL_Report_Print_Automation

下载地址:
<https://github.com/1595258509/QCBL_Report_Print_Automation/releases/>

`user.json`文件中的是默认的学号和密码，可以在里面直接先输好\
使用的话直接按照要求一步步来就行了\
按课程打印中的卷数就是左边那一栏

现仅支持内网环境下使用

## Python版本>3.7

| 用到的python模块 | 用途 |
| :-- | :-- |
| `PySimpleGUI`   | GUI界面的搭建 |
| `pdfkit`        | 生成PDF |
| `requests`      | 用于发送HTTP请求 |
| `beautifulsoup4`| 用于解析HTML |

安装Python模块直接:

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

> `-i` 后面是使用清华大学镜像源加速下载

---

pdfkit是基于wkhtmltopdf的python封装，所以需要先安装wkhtmltopdf\
macOS用户可以直接使用Homebrew安装

```shell
brew install wkhtmltopdf
```

Windows用户就直接在官网下载安装：<https://wkhtmltopdf.org/downloads.html>

## 展望

[x] `BeautifulSoup`处理表格\
[x] 题目AC判断\
[x] 并发打印\
[ ] WebVPN登录\
[ ] 界面优化

因为比较懒，没有写注释，望谅解😭
