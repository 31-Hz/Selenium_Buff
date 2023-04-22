# # # # # # # # # # # # # # # # #
# -*- coding: utf-8 -*-         #
# @Project : Selenium-Buff      #
# @Time    : 2023/4/21          #
# @Author  : 31Hz               #
# @Email   : 2787723665@qq.com  #
# # # # # # # # # # # # # # # # #


# 导入对应的模块
# 时间模块
import time
# selenium模块
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
# 邮箱模块
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# 设定监控价格界限
set_price = 11
# 修改 "M4A4 | 黑色魅影 (久经沙场)"，即可更换要监控的商品
# 注意要保持格式与上面一致，最好是从buff官网上复制名称，不能有不一样的文字和符号


# 配置邮箱模块实现自动化发送
my_sender = 'xxxxxxxx@qq.com'  # 填写发信人的邮箱账号
my_pass = 'xxxxxxxx'  # 发件人邮箱授权码
my_user = 'xxxxxxxx@qq.com'  # 收件人邮箱账号


def mail():
    ret = True
    try:
        msg = MIMEText('发现有价格低于设定价格的商品', 'plain', 'utf-8')  # 填写邮件内容
        msg['From'] = formataddr(["xx", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['To'] = formataddr(["xx", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = "buff商品通知"  # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱授权码
        server.sendmail(my_sender, [my_user, ], msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


# 携带chrome本地cookie登录实现免登陆操作
# 注意：需要保证没有chrome浏览器正在打开，否则运行报错!!!
# 个人资料路径(chrome://version/，查看个人资料路径,去掉最后的‘\Default’)

# 加载配置数据
option = webdriver.ChromeOptions()
option.add_argument(r'--user-data-dir=C:\Users\HZ\AppData\Local\Google\Chrome\User Data')  # 设置成自己的数据目录
# 指定浏览器为无界面模式（要想使用有界面模式注释掉下面一行的代码即可）
option.add_argument('--headless=new')
# 启动浏览器配置
driver = webdriver.Chrome(options=option)

# 设置隐式等待时间最长为10s
driver.implicitly_wait(10)

# 打开buff
driver.get("https://buff.163.com/")

# 点击饰品市场
driver.find_element(By.XPATH, '//a[@href="/market/csgo"]').click()

# 在搜索栏中输入要监控的武器名称
driver.find_element(By.XPATH, '//span/input[@type="text" and @name="search"]').send_keys("AK-47 | 精英之作 (久经沙场)")

# 点击搜索按钮
driver.find_element(By.CSS_SELECTOR, '[id="search_btn_csgo"]').click()

# 点击查找出来的第一个
driver.find_element(By.XPATH, '//li/a[@title="AK-47 | 精英之作 (久经沙场)"]').click()

# 鼠标模拟：使价格按照从低到高排序
sel = driver.find_element(By.XPATH, '//div[@style="visibility: visible; width: 98px;"]')
action = ActionChains(driver)
action.move_to_element(sel).click().move_by_offset(0, 128).click().perform()

# 鼠标模拟：选择磨损区间
sel2 = driver.find_element(By.XPATH, '//h3[@id="custom_paintwear_show"]')
# 输入64选择该品质的第一档磨损，选择第二档需要加32即96，这里输入160即为选择第四档磨损
action.move_to_element(sel2).click().move_by_offset(0, 160).click().perform()


# 获取价格
price_list = []


def get_price():
    # 定位当前页面所有商品价格元素所在位置，并且存入prices变量
    prices = driver.find_elements(By.CSS_SELECTOR, 'div>strong[class="f_Strong"]')
    # 对prices中的每个价格进行操作
    for price in prices:
        # 获取价格元素的文本值并且删除价格前面的 "¥ "
        price2 = price.text.replace("¥ ", "")
        # 转换为浮点数存入price_list列表中
        price_list.append(float(price2))


# 调用一次函数获取价格列表
get_price()


# 对比获取的价格与设定的价格
key = False
while key is False:
    # 遍历price_list列表
    for price_val in price_list:
        # 当有商品的价格小于设定值时发送邮件
        if price_val < set_price:
            ret_val = mail()
            if ret_val:
                print("邮件发送成功")
                # 跳出循环
                key = True
                break
            else:
                print("邮件发送失败")

        # 如果price_list列表的最后一个商品价格依然大于设定的价格会进行以下操作并一直循环下去，直到出现低于设定价格的商品
        if price_list[len(price_list) - 1] >= set_price:
            # 等待10s后刷新页面
            time.sleep(10)
            driver.refresh()
            # 获取新的价格并且存入到price_list列表中
            get_price()

# 完成后退出浏览器
driver.quit()
