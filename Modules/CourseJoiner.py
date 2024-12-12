from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests

class CourseJoiner:

    def __init__(self, from_day:int, to_day:int, threads:int=10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://www.coursejoiner.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.course_joiner_coupon_links =[]

    def collect_course_joiner_coupon_links(self):

        while self.from_day <= self.to_day:

            html_page =requests.get(self.base_url+'/category/free-udemy/page/'+str(self.from_day)).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')

            div_tags =html_page_soup.find_all('div', {'class': 'td-module-thumb'})

            for div_tag in div_tags:
                a_tag =div_tag.find('a')
                if a_tag['href'].startswith(self.base_url+'/free-udemy/'):
                    self.course_joiner_coupon_links.append([a_tag['title'], a_tag['href']])

            self.from_day +=1

    def thread_coursejoiner_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a')

        for a_tag in a_tags:
            coupon_shortern_link =a_tag['href']

            if a_tag.text=='APPLY HERE':
                response =requests.get(coupon_shortern_link, allow_redirects=False)
                response_headers =response.headers
                coupon_shortern_link =response_headers.get('location')

                response =requests.get(coupon_shortern_link, allow_redirects=False)
                redirect_page_soup =BeautifulSoup(response.text, 'html.parser')
                span_tag =redirect_page_soup.find('span', {'id': 'url'})
                coupon_shortern_link =span_tag.text
                # print(coupon_shortern_link)
                
                response =requests.get(coupon_shortern_link, allow_redirects=False)
                response_headers =response.headers
                location =response_headers.get('location')
                if location and location.startswith('https://www.udemy.com/'):
                    self.coupons.append([offer[0], location])
                else:
                    self.unwanted_links.append(offer)        
                break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, course_joiner_urls):
        
        for course_joiner_url in course_joiner_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_coursejoiner_coupons_through_url, args=[course_joiner_url]).start()

        while len(self.course_joiner_coupon_links)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)


if __name__ == '__main__':
    courseJoiner =CourseJoiner(1, 1)
    courseJoiner.collect_course_joiner_coupon_links()
    courseJoiner.collect_courses(courseJoiner.course_joiner_coupon_links)
    print(courseJoiner.coupons)



