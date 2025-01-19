from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests, urllib

class CursosDev:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://en.cursosdev.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.cursosdev_course_urls =[]

    def collect_cursosdev_course_urls(self):

        while self.from_day <= self.to_day:
            html_page =requests.get(self.base_url+'/coupons?page='+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': ''})

            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                if not a_tag: continue
                card_header_div =a_tag.find('div')
                if not card_header_div: continue
                discount_div =card_header_div.find('div')
                if discount_div and '-100%' in discount_div.text.strip('\n\t '):
                    h2_tag =a_tag.find('h2')
                    course_name =h2_tag.text.strip('\n\t ')

                    offer =[course_name, a_tag['href']]
                    if offer not in self.cursosdev_course_urls:
                        self.cursosdev_course_urls.append(offer)

            self.from_day +=1

    def thread_cursosdev_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a')

        for a_tag in a_tags:
            if ('Get Coupon' in a_tag.text.strip('\n\t ')):
                coupon_link =urllib.parse.unquote(a_tag['href'].split('murl=')[-1])
                if coupon_link.startswith('https://www.udemy.com/') and '?couponCode=' in coupon_link:
                    self.coupons.append([offer[0], coupon_link])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, cursosdev_urls):
        
        for cursosdev_url in cursosdev_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_cursosdev_coupons_through_url, args=[cursosdev_url]).start()

        while len(self.cursosdev_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    cursosDev =CursosDev(1, 1)
    cursosDev.collect_cursosdev_course_urls()
    cursosDev.collect_courses(cursosDev.cursosdev_course_urls)
    print(cursosDev.coupons)