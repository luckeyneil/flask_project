# -*- coding:utf-8 -*-


from flask import Blueprint
from flask import current_app

html = Blueprint("html", __name__)


@html.route('/<re(".*"):file_name>')
def web_html(file_name):
    # 3中情况，
    # 1.请求的是根路径，自动转到index.html
    # 2.请求的是favicon.ico路径，直接放在静态文件根目录下
    # 3.请求的是其他普通路径，到静态文件的html文件夹下找

    if not file_name:
        file_name = 'index.html'

    if file_name != 'favicon.ico':
        file_name = 'html/' + file_name

    print file_name
    return current_app.send_static_file(file_name)
