import requests
from bs4 import BeautifulSoup

class YoFreeSamples:

    def __init__(self):
        self.base_url ='https://yofreesamples.com'
        self.coupons =[]

    def collect_coupons(self):
        html_page =requests.get(self.base_url+'/courses/free-discounted-udemy-courses-list/').text
        html_page_soup =BeautifulSoup(html_page, 'html.parser')

        a_tags =html_page_soup.find_all('a', {'class': 'external_link_title'})

        for a_tag in a_tags:
            course_name =a_tag.text
            link =a_tag['href']
            if (link and link.startswith('https://www.udemy.com/')):
                self.coupons.append([course_name, link])

if __name__ == '__main__':
    yoFreeSamples =YoFreeSamples()
    yoFreeSamples.collect_coupons()
    print(yoFreeSamples.coupons)