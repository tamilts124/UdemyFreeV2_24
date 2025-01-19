from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class CouponsEagle:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://www.couponseagle.com/'
        self.coupons =[]
        self.unwanted_links =[]
        self.couponseagle_course_urls =[]

    def collect_couponseagle_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/page/'+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': 'newsdetail newstitleblock rh_gr_right_sec'})

            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                course_name =a_tag.text.strip('\n\t ')
                self.couponseagle_course_urls.append([course_name, a_tag['href']])

            self.from_day +=1

    def thread_couponseagle_coupons_through_url(self, offer):
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

    def collect_courses(self, couponseagle_urls):
        
        for couponseagle_url in couponseagle_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_couponseagle_coupons_through_url, args=[couponseagle_url]).start()

        while len(self.couponseagle_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    couponsEagle =CouponsEagle(1, 1)
    couponsEagle.collect_couponseagle_course_urls()
    couponsEagle.collect_courses(couponsEagle.couponseagle_course_urls)
    print(couponsEagle.coupons)