#千锤百炼实验报告自动化打印
=================
## QCBL_Report_Print_Automation

**Python版本：3.9**

| 用到的python模块                       |                       |
|-----------------------------------|:----------------------| 
| os                                | 用于处理文件和目录             |  
| re                                | 用于处理正则表达式             | 
| PySimpleGUI                       | GUI界面的搭建              |
| pdfkit                            | 生成PDF                 |
| selenium                          | WEB自动化工具              |
| [Microsoft Edge Driver(Chromium)](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)| 用于selenium和Edge浏览器的连接 |

------------

pdfkit是基于wkhtmltopdf的python封装，所以需要先安装wkhtmltopdf\
Mac os用户可以直接使用Homebrew安装
```Zsh
brew install wkhtmltopdf
```
Windows就直接在官网下载安装即可：[点我](https://wkhtmltopdf.org/downloads.html)

---------

如果要使用其他浏览器,在下列行数中进行修改即可\
要记得安装相应浏览器的driver：\
Driver 可以在这个网页下载：[点我](https://liushilive.github.io/github_selenium_drivers/index.html)
```Python3
from selenium.webdriver.edge import webdriver
from selenium.webdriver.edge.options import Options
```

```Python3
self.options = Options()
self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
self.driver = webdriver.WebDriver(options=self.options)
```
例如要改成Chrome浏览器，就改成这样\
```Python3
from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.options import Options
```

```Python3
self.options = Options()
self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
self.driver = webdriver.WebDriver(options=self.options)
```