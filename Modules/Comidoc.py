from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests, json

class Comidoc:

    def __init__(self):
        self.base_url ='https://comidoc.com/'
        self.coupons =[]

    def collect_coupons(self):

        html_page =requests.get(self.base_url).text
        html_split =list(filter(lambda i: 'discountValue' in i and 'remainingUses' in i, html_page.split('<script>')))

        if len(html_split)==0:
            raise Exception('Site Updated: have to update the scraping logic.')

        js_content =html_split[0].split(')</script>')[0].split('(', 1)[1]

        json_data =json.loads(js_content)[-1].split(':', 1)[-1]

        items =json.loads(json_data)[-1]['coupons']

        for item in items:
            course_name =item.get('course').get('detail')[0].get('title')
            coupon_link =f"https://www.udemy.com/course{item.get('course').get('cleanUrl')}?couponCode={item.get('code')}"
            self.coupons.append([course_name, coupon_link])

if __name__ == '__main__':
    comidoc =Comidoc()
    comidoc.collect_coupons()
    print(comidoc.coupons)