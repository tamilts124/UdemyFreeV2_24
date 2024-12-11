import requests
from bs4 import BeautifulSoup
from threading import Thread

class UdemyFreebies:

    def __init__(self, from_page:int, to_page:int, threads:int =10):
        self.from_page =from_page
        self.to_page =to_page
        self.coupons =[]
        self.threads =0
        self.mthreads =threads

        self.freebies_course_links =[]
        self.base_url ='https://www.udemyfreebies.com'

    def collect_freebies_course_links(self):
        while (self.from_page<self.to_page+1):
            html_page =requests.get(self.base_url+'/free-udemy-courses/'+str(self.from_page)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            a_tags =html_page_soup.find_all('a')
            for a_tag in a_tags:
                if a_tag.text.strip()=='Coupon Detail':
                    self.freebies_course_links.append(a_tag['href'])
            self.from_page +=1
        self.freebies_course_links =list(set(self.freebies_course_links))

    def get_udemy_location_header_from_url(self, offer_link):
        freebies_response_header =requests.get(offer_link, allow_redirects=False).headers
        self.coupons.append(freebies_response_header['location'])
        self.threads -=1

    def collect_coupons(self, freebies_links:list):

        for freebies_link in freebies_links:
            partial_offer_link =freebies_link.split(self.base_url+'/free-udemy-course')[-1]
            offer_link =self.base_url+'/out'+partial_offer_link
            while (self.threads>=self.mthreads): pass
            self.threads+=1
            Thread(target=self.get_udemy_location_header_from_url, args=[offer_link]).start()
        
        while len(self.coupons)!=len(self.freebies_course_links): pass

        self.coupons =list(set(self.coupons))

if __name__ == '__main__':
    udemyFreebies =UdemyFreebies(1,1)
    udemyFreebies.collect_freebies_course_links()
    udemyFreebies.collect_coupons(udemyFreebies.freebies_course_links)
    print(udemyFreebies.coupons)
















