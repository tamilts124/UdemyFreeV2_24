from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class DiscUdemy:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://www.discudemy.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.discudemy_course_urls =[]

    def collect_discudemy_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/all/'+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            a_tags =html_page_soup.find_all('a', {'class': 'card-header'})

            for a_tag in a_tags:
                self.discudemy_course_urls.append([a_tag.text, a_tag['href']])

            self.from_day +=1

    def thread_disudemy_coupons_through_url(self, offer):
        partial_course_url = offer[1].split(self.base_url)[-1].split('/')[-1]
        disudemy_link =self.base_url+'/go/'+partial_course_url
        html_page =None
        while not html_page:
            try:
                html_page =requests.get(disudemy_link).text
            except Exception: continue

        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a')

        for a_tag in a_tags:
            # print(a_tag)
            coupon_link =a_tag['href']

            if coupon_link.startswith('https://www.udemy.com/'):
                self.coupons.append([offer[0], coupon_link])
                break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, disudemy_urls):
        
        for disudemy_url in disudemy_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_disudemy_coupons_through_url, args=[disudemy_url]).start()

        while len(self.discudemy_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)


if __name__ == '__main__':
    discUdemy =DiscUdemy(1, 1)
    discUdemy.collect_discudemy_course_urls()
    discUdemy.collect_courses(discUdemy.discudemy_course_urls)
    print(discUdemy.coupons)