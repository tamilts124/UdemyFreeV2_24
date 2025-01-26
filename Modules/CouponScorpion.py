from threading import Thread
from time import sleep
from bs4 import BeautifulSoup
import requests, json, re
from urllib.parse import unquote

class CouponScorpion:
    
    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://couponscorpion.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.couponscorpion_course_urls =[]
        self.headers ={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0'}

    def collect_couponscorpion_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/category/100-off-coupons/page/'+str(self.from_day), headers=self.headers).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': 'newstitleblock'})

            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                self.couponscorpion_course_urls.append([a_tag.text, a_tag['href']])
            self.from_day +=1

    def thread_couponscorpion_coupons_through_url(self, offer):
        html_page =requests.get(offer[1], headers=self.headers).text

        # old method

        # sf_offer_url =re.findall("var sf_offer_url = '.*';", html_page)
        # sf_offer_url =re.findall('.*', sf_offer_url[0])[0].split("'")[1]

        # data =f"go={sf_offer_url}&a={0}"
        # url_data =unquote(data)
        # url =self.base_url+'/scripts/udemy/out.php?'+url_data

        # new update
        html_page_soup =BeautifulSoup(html_page, 'html.parser')
        a_tags =html_page_soup.find_all('a', {'class': 're_track_btn'})

        for a_tag in a_tags:
            if 'GET COUPON CODE' in a_tag.text.strip('\n\t\r '):
                url =a_tag['href']
                response_headers =requests.get(url, headers=self.headers, allow_redirects=False).headers
                print(response_headers['location'])

                if response_headers['location'].startswith('https://www.udemy.com/'):
                    self.coupons.append([offer[0], response_headers['location']])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, couponscorpion_urls):
        
        for couponscorpion_url in couponscorpion_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_couponscorpion_coupons_through_url, args=[couponscorpion_url]).start()

        while len(self.couponscorpion_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)


if __name__ == '__main__':
    couponScorpion =CouponScorpion(1, 1)
    couponScorpion.collect_couponscorpion_course_urls()
    couponScorpion.collect_courses(couponScorpion.couponscorpion_course_urls)
    print(couponScorpion.coupons)
