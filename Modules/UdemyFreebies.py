import requests
from bs4 import BeautifulSoup
from threading import Thread

class UdemyFreebies:

    def __init__(self, from_page:int, to_page:int, threads:int =10):
        self.from_page =from_page
        self.to_page =to_page
        self.coupons =[]
        self.waste_coupons =[]
        self.threads =0
        self.mthreads =threads

        self.freebies_course_links =[]
        self.base_url ='https://www.udemyfreebies.com'

    def collect_freebies_course_links(self):
        while (self.from_page<self.to_page+1):
            html_page =requests.get(self.base_url+'/free-udemy-courses/'+str(self.from_page)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': 'coupon-name'})
            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                self.freebies_course_links.append([a_tag.text, a_tag['href']])
            self.from_page +=1

    def thread_udemy_location_fetch_from_url(self, offer_name, offer_link):
        freebies_response_header =requests.get(offer_link, allow_redirects=False).headers
        self.coupons.append([offer_name, freebies_response_header['location']])
        self.threads -=1

    def collect_coupons(self, freebies_links:list):

        for freebies_link in freebies_links:
            partial_offer_link =freebies_link[1].split(self.base_url+'/free-udemy-course')[-1]
            offer_link =self.base_url+'/out'+partial_offer_link
            while (self.threads>=self.mthreads): pass
            self.threads+=1
            Thread(target=self.thread_udemy_location_fetch_from_url, args=[freebies_link[0], offer_link]).start()
        
        while len(self.coupons)!=len(self.freebies_course_links): pass


if __name__ == '__main__':
    udemyFreebies =UdemyFreebies(1,1)
    udemyFreebies.collect_freebies_course_links()
    udemyFreebies.collect_coupons(udemyFreebies.freebies_course_links)
    print(udemyFreebies.coupons)
















