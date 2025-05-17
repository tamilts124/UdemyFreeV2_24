from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class RealDiscount:

    def __init__(self, from_day:int, to_day:int, threads:int=10):
        self.from_day =from_day
        self.to_day =to_day
        self.cdn_url ='https://cdn.real.discount/api/courses?limit=14&sortBy=sale_start&'
        self.coupons =[]
        self.unwanted_links =[]

    def collect_coupons(self):

        while self.from_day <= self.to_day:

            json_data =requests.get(self.cdn_url+'/?page='+str(self.from_day)).json()
            items =json_data.get('items')
            for item in items:
                course_url =item.get('url')
                if item.get('sale_price')==0 and course_url.startswith('https://www.udemy.com/'):
                    self.coupons.append([item.get('name'), course_url])
                else:
                    self.unwanted_links.append([item.get('name'), course_url])
            self.from_day +=1

if __name__ == '__main__':
    realDiscount =RealDiscount(1, 1)
    realDiscount.collect_coupons()
    print(realDiscount.coupons)



