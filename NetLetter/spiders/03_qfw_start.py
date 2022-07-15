import csv

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)


def Qfw(url):
    driver.get(url + "/tycoon")
    file = open("3_qfw.csv", 'a+', newline='', encoding='utf-8')
    fieldnames = ['url', 'username']
    writer = csv.DictWriter(f=file, fieldnames=fieldnames)
    writer.writeheader()
    #
    try:
        if driver.find_element_by_class_name("warncontenter"):
            pass
    except selenium.common.exceptions.NoSuchElementException  as e:
        print(e)
    count = driver.find_element_by_xpath('/html/body/div[3]/div[3]/div[1]/span').text
    count = int(count)
    pages = count / 20
    if count < 20:
        page_ = 1
    else:
        page_ = int(pages) + 1
    for page in range(1, page_):
        url_ = url + "/tycoon/n%d" % page
        driver.get(url_)
        user_list = driver.find_elements_by_xpath('//*[@id="find_broker_lists"]/ul/li')
        for i in user_list:
            for d in i.find_elements_by_xpath('./div[1]/div[1]/p/b/a'):
                print(d.text, d.get_attribute('href'))
                writer.writerow({"url": d.text, "username": d.get_attribute('href')})


if __name__ == '__main__':
    qfw_list = ["https://guangzhou.qfang.com", "https://shenzhen.qfang.com/", "https://nanjing.qfang.com/",
                "https://zhuhai.qfang.com/", "https://qingdao.qfang.com/", "https://shanghai.qfang.com/", ]

    for url in qfw_list:
        Qfw(url)
