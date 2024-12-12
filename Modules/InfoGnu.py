from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class InfoGnu:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://infognu.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.infognu_course_urls =[]

    def collect_infognu_course_urls(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/courses/?category=100%-off&page='+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            a_tags =html_page_soup.find_all('a', {'class': 'uk-link-reset'})

            for a_tag in a_tags:
                course_name =a_tag.find('div', {'class': 'card-body'}).find('div').text.strip('\t\n ')
                self.infognu_course_urls.append([course_name, self.base_url+a_tag['href']])

            self.from_day +=1

    def thread_infognu_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a')

        for a_tag in a_tags:
            if (a_tag.text.strip()=='Take this course'):
                coupon_link =a_tag['href'].split('?link=')[-1]
                if coupon_link.startswith('https://www.udemy.com/'):
                    self.coupons.append([offer[0], coupon_link])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, infognu_urls):
        
        for infognu_url in infognu_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_infognu_coupons_through_url, args=[infognu_url]).start()

        while len(self.infognu_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    infoGnu =InfoGnu(1, 1)
    infoGnu.collect_infognu_course_urls()
    infoGnu.collect_courses(infoGnu.infognu_course_urls)
    print(infoGnu.coupons)