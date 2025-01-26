from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class ScrollCoupons:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://scrollcoupons.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.scrollcoupons_course_urls =[]

    def collect_scrollcoupons_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/store/udemy/100-off/'+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tag =html_page_soup.find('div', {'class': 'all'})
            a_tags =div_tag.find_all('a')

            for a_tag in a_tags:
                course_name =a_tag.text.strip('\n\t\r ').split('\n')[3]
                # print(course_name)
                self.scrollcoupons_course_urls.append([course_name, a_tag['href']])

            self.from_day +=1

    def thread_scrollcoupons_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a', {'class': 'deal_btn'})

        for a_tag in a_tags:
            if (a_tag.text.strip('\n\t ')=='See Code'):
                coupon_link =a_tag['href']
                if coupon_link.startswith('https://www.udemy.com/'):
                    self.coupons.append([offer[0], coupon_link])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, scrollcoupons_urls):
        
        for scrollcoupons_url in scrollcoupons_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_scrollcoupons_coupons_through_url, args=[scrollcoupons_url]).start()

        while len(self.scrollcoupons_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    scrollCoupons =ScrollCoupons(1, 1)
    scrollCoupons.collect_scrollcoupons_course_urls()
    scrollCoupons.collect_courses(scrollCoupons.scrollcoupons_course_urls)
    print(scrollCoupons.coupons)