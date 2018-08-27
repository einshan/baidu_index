# -*- coding: utf-8 -*-
"""
Created on Sun Aug 26 22:48:06 2018

@author: asus
"""

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from PIL import Image
import pytesseract
import getpass

# 登陆部分


def login(browser, userName, password):
    #输入 url
    loginUrl = "https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F"
    # 跳转到登陆界面
    browser.get(loginUrl)
    # 超时限制
    timeout = 120  # seconds
    time.sleep(10)
    try:
         # 等待准备点击
        switchLoginMethod = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.ID, 'TANGRAM__PSP_3__footerULoginBtn')))
        switchLoginMethod.click()
        # 等待输入字段就绪
        userNameField = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_3__userName')))
        userNameField.clear()
        userNameField.send_keys(userName)
        passwordField = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.ID, 'TANGRAM__PSP_3__password')))
        passwordField.clear()
        passwordField.send_keys(password)
        # 提交
        submitButton = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((By.ID, 'TANGRAM__PSP_3__submit')))
        submitButton.click()

    except TimeoutException:
        print("Loading took too much time!")


# 爬取百度指数
def getindex(browser, keyword, day):
    # 设置url和超时限制
    indexurl = "http://index.baidu.com"
    indexTimeout = 60
    browser.get(indexurl)
    # 等待页面准备就绪
    searchField = WebDriverWait(browser, indexTimeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.search-input')))
    # 清空字段并输入关键词
    searchField.clear()
    searchField.send_keys(keyword)
    # 找到并点击按钮
    button = WebDriverWait(browser, indexTimeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.search-input-operate')))
    button.click()

    # 放大屏幕
    time.sleep(5)
    # 找到日期
    sel = '//a[@rel="' + str(day) + '"]'
    dayButton = WebDriverWait(browser, indexTimeout).until(
        EC.element_to_be_clickable((By.XPATH, sel)))
    dayButton.click()
    # 设置获取图形框
    xoyelementReady = False
    while xoyelementReady == False:
        try:
            xoyelement = browser.find_elements_by_css_selector("#trend rect")[
                2]
            xoyelementReady = True
        except:
            time.sleep(2)
            print('xoyelement not ready yet')

    num = 0
    x_0 = 3
    y_0 = 30
    index = []
    # 获取图形框宽度
    xoyelement_length = xoyelement.size['width']
    xoyelement_height = xoyelement.size['height']
    if day == "all":
        day = 1000000
    # 用selenium库来模拟鼠标滑动悬浮
    ActionChains(browser).move_to_element_with_offset(
        xoyelement, 250, 40).perform()
    time.sleep(2)
    moveTimeout = 5
    # 上下移动
    up_down = True
    try:
        # 按照天数进行循环
        for i in range(day):
            print(str(x_0)+' '+str(y_0))
            # 将光标移动到下一点
            ActionChains(browser).move_to_element_with_offset(
                xoyelement, x_0, y_0).perform()
            # 构造规则
            if day == 7:
                x_0 = x_0 + (xoyelement_length-10)/6
                if up_down == True:
                    y_0 = y_0 - 25
                else:
                    y_0 = y_0 + 25
                up_down = ~up_down
            elif day == 30:
                x_0 = x_0 + (xoyelement_length-10)/29
                if up_down == True:
                    y_0 = y_0 - 25
                else:
                    y_0 = y_0 + 25
                up_down = ~up_down
            elif day == 90:
                x_0 = x_0 + (xoyelement_length-10)/89
                if up_down == True:
                    y_0 = y_0 - 25
                else:
                    y_0 = y_0 + 25
                up_down = ~up_down
            elif day == 180:
                x_0 = x_0 + (xoyelement_length-10)/179
                if up_down == True:
                    y_0 = y_0 - 25
                else:
                    y_0 = y_0 + 25
                up_down = ~up_down
            elif day == 1000000:
                x_0 = x_0 + 3.37222222
                if up_down == True:
                    y_0 = y_0 - 25
                else:
                    y_0 = y_0 + 25
                up_down = ~up_down

            # 获取屏幕大小
            screen = browser.find_element_by_xpath('//html')
            screenSize = screen.size

            time.sleep(2)
            try:
                 # 等待数据划分完成
                imgelement = WebDriverWait(browser, moveTimeout).until(
                    EC.visibility_of_element_located((By.XPATH, '//div[@id="viewbox"]/div[2]')))
                time.sleep(1)
                locations = imgelement.location
                # 跨浏览器兼容
                scroll = browser.execute_script("return window.scrollY;")
                top = locations['y'] - scroll + 219  # + navSize['height']
                sizes = imgelement.size
                # 截图范围
                rangle = (
                    int(locations['x']), int(top),
                    int(locations['x'] + sizes['width'] + 1), int(top + sizes['height'] + 1))
                # 保存屏幕截图
                path = "./" + str(num)
                browser.save_screenshot(str(path) + ".png")
                img = Image.open(str(path) + ".png")
                img = img.resize((screenSize['width'], screenSize['height']))
                # 输出img
                jpg = img.crop(rangle)
                jpg = jpg.convert('RGB')
                # 输出jpg
                jpg.save(str(path) + ".jpg")
                # 放大图片
                jpgzoom = Image.open(str(path) + ".jpg")
                (x, y) = jpgzoom.size
                x_s = x*2
                y_s = y*2
                out = jpgzoom.resize((x_s, y_s), Image.ANTIALIAS)
                # 保存
                out.save(path + 'zoom.jpg', 'png', quality=95)
                # 图片识别
                try:
                    image = Image.open(str(path) + "zoom.jpg")
                    code = pytesseract.image_to_string(image)
                    if code:
                        index.append(code)
                    else:
                        index.append("")
                except Exception as err:
                    print(err)
                    index.append("")
                num = num + 1
            except:
                i = i-1

    except Exception as err:
        print(err)

    print(index)
    # 将结果保存在文件中
    file = open("./index.txt", "w")
    for item in index:
        text = ''.join([x for x in item if x.isdigit()])
        file.write(str(text) + "\n")
    file.close()


if __name__ == "__main__":
    # 使用chrome浏览器

    # 调试部分
    needLogin = True
    try:
        browser = webdriver.Remote(
            command_executor='http://127.0.0.1:65404', desired_capabilities={})
        browser.session_id = '7edc96d892f65946d492d418600798cc'
        browser.get('http://index.baidu.com')
        needLogin = False
    except:
        browser = webdriver.Chrome()
        executor_url = browser.command_executor._url
        session_id = browser.session_id
        print(executor_url)
        print(session_id)

    # 登陆
    if needLogin:
        userName = input("请输入用户名：")
        password = getpass.getpass('请输入密码：')
        login(browser, userName, password)
        input("请检查登陆状态，如果已经登陆， 请按enter， 否则请手动登陆，然后按enter")
    # 查询关键字
    keyword = input("请输入查询关键字：")
    day = int(input("请输入查询天数"))

    if day <= 7:
        day = 7
    elif day <= 30:
        day = 30
    elif day <= 90:
        day = 90
    elif day <= 180:
        day = 180
    else:
        day = "all"
    getindex(browser, keyword, day)
