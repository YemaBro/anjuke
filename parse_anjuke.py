from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pyquery import PyQuery as pq
import pymongo

'''
通过拓展添加selenium下的代理。
'''
# from tool import create_proxyauth_extension
#
# proxyauth_plugin_path = create_proxyauth_extension(
#     proxy_host="XXXXX.com",
#     proxy_port=9020,
#     proxy_username="XXXXXXX",
#     proxy_password="XXXXXXX"
# )

# co = webdriver.ChromeOptions()
# co.add_argument("--start-maximized")
# co.add_extension(proxyauth_plugin_path)
# driver = webdriver.Chrome(chrome_options=co)


client = pymongo.MongoClient('localhost')
db = client['anjuke']

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def save_to_mongo(i):
    try:
        if db['zufang'].insert_one(i):
            print('插入数据成功：', i)
    except Exception:
        print('插入数据失败：', i)


def info_msg(page):
    try:
        base_url = 'https://hz.zu.anjuke.com/p{page}'.format(page=page)
        browser.get(base_url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#list-content .zu-itemmod')))
        html = browser.page_source
        doc = pq(html)
        detail_link = doc('#list-content .zu-itemmod').items()
        for item in detail_link:
            link = item.attr('link')
            detail_msg(link)
    except TimeoutException:
        return info_msg(page)


def detail_msg(link):
    try:
        browser.get(link)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mainbox .lbox .house-info-zufang')))
        html = browser.page_source
        doc = pq(html)
        msg = doc('.mainbox .lbox .house-info-zufang').items()
        for i in msg:
            item = {
                'price': i('li').eq(0).find('.price em').text(),
                'mode': i('li').eq(0).find('.type').text(),
                'huxing': i('li').eq(1).find('.info').text(),
                'mianji': i('li').eq(2).find('.info').text(),
                'chaoxiang': i('li').eq(3).find('.info').text(),
                'louceng': i('li').eq(4).find('.info').text(),
                'zhuangxiu': i('li').eq(5).find('.info').text(),
                'type': i('li').eq(6).find('.info').text(),
                'xiaoqu': i('li').eq(7).find('a').text(),
                'yaoqiu': i('li').eq(8).find('.info').text()
            }
            save_to_mongo(item)
    except TimeoutException:
        return detail_msg(link)


def main():
    try:
        for p in range(1, 51):
            p = str(p)
            info_msg(p)
    except Exception:
        print('发生错误')
    finally:
        browser.close()


if __name__ == '__main__':
    main()
