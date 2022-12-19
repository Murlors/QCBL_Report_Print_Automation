# 千锤百炼实验报告自动化打印

## QCBL_Report_Print_Automation

下载地址：
[https://github.com/1595258509/QCBL_Report_Print_Automation/releases/](https://github.com/1595258509/QCBL_Report_Print_Automation/releases/)

`user.json`文件中的是默认的学号和密码，可以在里面直接先输好\
使用的话直接按照要求一步步来就行了\
按课程打印中的卷数就是左边那一栏

## Python版本：3.9

| 用到的python模块 |                    |
| :--              | :--                |
| os               | 用于处理文件和目录 |
| re               | 用于处理正则表达式 |
| PySimpleGUI      | GUI界面的搭建      |
| pdfkit           | 生成PDF            |
| selenium         | WEB自动化工具      |

安装Python模块直接：

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

>`-i` 后面是使用清华大学镜像源加速下载

---

pdfkit是基于wkhtmltopdf的python封装，所以需要先安装wkhtmltopdf\
macOS用户可以直接使用Homebrew安装

```shell
brew install wkhtmltopdf
```

Windows用户就直接在官网下载安装：[https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)

---

默认浏览器是Chromium内核的Edge浏览器，如果要使用其他浏览器，在下列行数中进行修改即可

```python
from webdriver_manager.microsoft import EdgeChromiumDriverManager
```

```python
self.driver = webdriver.ChromiumEdge(EdgeChromiumDriverManager(cache_valid_range=7).install())
```

如果是macOS使用Safari要先打开Safari开发选项卡中的允许远程自动化，Safari不需要安装WebDriver,但是需要修改上述代码成

```python
self.driver = webdriver.Safari()
```

若要改成Chrome浏览器

```python
from webdriver_manager.chrome import ChromeDriverManager
```

```python
self.driver = webdriver.Chrome(ChromeDriverManager(cache_valid_range=7).install())
```

以此类推，改成Firefox

```python
from webdriver_manager.firefox import DriverManager
```

```python
self.driver = webdriver.Firefox(DriverManager(cache_valid_range=7).install())
```

## 展望

+ `BeautifulSoup`优化速度
+ 题目AC判断
+ 多线程

因为比较懒，没有写注释，望谅解😭
