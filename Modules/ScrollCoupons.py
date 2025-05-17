from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

requests =requests.Session()

requests.headers ={
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
}

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
        self.timeout =2

    def collect_scrollcoupons_course_urls(self):

        while self.from_day <= self.to_day:
            html_page =requests.get(self.base_url+'/store/udemy/100-off/'+str(self.from_day), allow_redirects=False, timeout=self.timeout).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tag =html_page_soup.find('div', {'class': 'all'})
            a_tags =div_tag.find_all('a')

            for a_tag in a_tags:
                course_name =a_tag['title'].strip('\n\t\r ')
                # print(course_name)
                self.scrollcoupons_course_urls.append([course_name, a_tag['href']])

            self.from_day +=1

    def thread_scrollcoupons_coupons_through_url(self, offer):
        html_page =requests.get(offer[1], timeout=self.timeout).text
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