from bs4 import BeautifulSoup
from threading import Thread
from time import sleep
import requests, json

class CourseCouponClub:

    def __init__(self, from_day:int, to_day:int, threads:int =10):
        self.from_day =from_day
        self.to_day =to_day
        self.mthreads =threads
        self.threads =0
        self.base_url ='https://coursecouponclub.com'
        self.coupons =[]
        self.unwanted_links =[]
        self.coursecouponclub_course_urls =[]

    def collect_coursecouponclub_course_urls(self):
        home_page =requests.get(self.base_url).text
        security_code =home_page.split('"filternonce":"')[1].split('"')[0]

        while self.from_day <= self.to_day:

            data ={
                'action': 're_filterpost',
                'filterargs[post_type]': 'post',
                'filterargs[posts_per_page]': '10',
                'filterargs[orderby]': 'modified',
                'template': 'column_grid',
                'offset': (self.from_day*10)-10,
                'innerargs[columns]': '5_col',
                'security': security_code
            }

            html_page =requests.post(self.base_url+'/wp-admin/admin-ajax.php', data=data).text
            html_page_soup =BeautifulSoup(html_page, 'html.parser')
            h2_tags =html_page_soup.find_all('h2')

            for h2_tag in h2_tags:
                a_tag =h2_tag.find('a')
                course_name =a_tag.text.strip('\n\t ')
                self.coursecouponclub_course_urls.append([course_name, a_tag['href']])

            self.from_day +=1

    def thread_coursecouponclub_coupons_through_url(self, offer):
        html_page =requests.get(offer[1]).text
        hmtl_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =hmtl_page_soup.find_all('a', {'class': 're_track_btn'})

        for a_tag in a_tags:
            if (a_tag.text.strip('\n\t ') in ('Enroll Now', 'Claim Udemy Coupon')):
                coupon_link =a_tag['href'].split('murl=')[1]
                if coupon_link.startswith('https://www.udemy.com/'):
                    self.coupons.append([offer[0], coupon_link])
                    break
        else:
            self.unwanted_links.append(offer)

        self.threads -=1

    def collect_courses(self, coursecouponclub_urls):
        
        for coursecouponclub_url in coursecouponclub_urls:
            while self.threads >=self.mthreads: sleep(0.2)
            self.threads +=1
            Thread(target=self.thread_coursecouponclub_coupons_through_url, args=[coursecouponclub_url]).start()

        while len(self.coursecouponclub_course_urls)>len(self.coupons)+len(self.unwanted_links): sleep(0.2)

if __name__ == '__main__':
    courseCouponClub =CourseCouponClub(1, 1)
    courseCouponClub.collect_coursecouponclub_course_urls()
    courseCouponClub.collect_courses(courseCouponClub.coursecouponclub_course_urls)
    print(courseCouponClub.coupons)