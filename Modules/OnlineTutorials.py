from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class OnlineTutorials:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://www.onlinetutorials.org'
        self.coupons =[]
        self.unwanted_links =[]
        self.onlinetutorials_course_urls =[]

    def collect_onlinetutorials_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/page/'+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': 'newsdetail newstitleblock rh_gr_right_sec'})

            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                course_name =a_tag.text.strip('\n\t ')
                self.onlinetutorials_course_urls.append([course_name, a_tag['href']])

            self.from_day +=1

    def thread_onlinetutorials_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a', {'class': 're_track_btn'})

        for a_tag in a_tags:
            if (a_tag.text.strip('\n\t ')=='Redeem Coupon'):
                coupon_link =a_tag['href']
                if coupon_link.startswith('https://www.udemy.com/') and '?couponCode=' in coupon_link:
                    self.coupons.append([offer[0], coupon_link])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, onlinetutorials_urls):
        
        for onlinetutorials_url in onlinetutorials_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_onlinetutorials_coupons_through_url, args=[onlinetutorials_url]).start()

        while len(self.onlinetutorials_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    onlineTutorials =OnlineTutorials(1, 1)
    onlineTutorials.collect_onlinetutorials_course_urls()
    onlineTutorials.collect_courses(onlineTutorials.onlinetutorials_course_urls)
    print(onlineTutorials.coupons)