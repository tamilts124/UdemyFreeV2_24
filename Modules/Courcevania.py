import cloudscraper, json
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep


requests =cloudscraper.CloudScraper()
class Coursevania:
    def __init__(self, max_threads:int=5):
        # coursevania course page links
        self.offers_link =[]
        self.coupons =[]

        #token
        self.nonces ={}

        self.threads =0
        self.max_threads =max_threads
        self.get_nonces()

    def get_nonces(self):
        course_page= requests.get("https://coursevania.com/courses/").text
        cpage =list(filter(lambda e: "stm_lms_nonces" in e, course_page.split('<script>')))
        if len(cpage)>0:
            nonces =cpage[0].split('stm_lms_nonces =')[1].split(';')[0].strip()
            self.nonces =json.loads(nonces)

    def get_home_page_offerslink(self, from_page:int, to_page:int):
        for index in range(from_page, to_page):
            home_page =requests.get(f"https://coursevania.com/wp-admin/admin-ajax.php?offset={index}"+r"&args={%22image_size%22:%22250x250%22,%22per_row%22:%224%22,%22posts_per_page%22:%2212%22,%22class%22:%22archive_grid%22}&action=stm_lms_load_content"+f"&nonce={self.nonces['load_content']}&sort=date_high").json()
            course_cards =BeautifulSoup(home_page['content'], 'html.parser').findAll('div', {'class': 'stm_lms_courses__single'})
            for card in course_cards:
                h5_tag =card.find('h5')
                anger_tag =card.find('a')
                if anger_tag and anger_tag['href']: self.offers_link.append([h5_tag.text, anger_tag['href']])

    def thread_get_coupons_by_offerslink(self, offer_link:list):
        offer_page =requests.get(offer_link[1]).text
        self.threads -=1
        offer =BeautifulSoup(offer_page, 'html.parser')
        anger_tag =offer.find('a', {'class': 'masterstudy-button-affiliate__link'})
        self.coupons.append([offer_link[0], anger_tag['href']])

    def get_coupons_by_offerslink(self, offers_link:list):
        for offer_link_index in range(len(offers_link)):
            Thread(target=self.thread_get_coupons_by_offerslink, args=[offers_link[offer_link_index]]).start()
            self.threads +=1
            while (self.threads>=self.max_threads or (offer_link_index==len(offers_link)-1 and len(offers_link)>len(self.coupons))):
                sleep(0.2)
    

if __name__ == '__main__':
    coursevania =Coursevania()
    coursevania.get_home_page_offerslink(0, 2)
    # print(coursevania.offers_page_links)
    coursevania.get_coupons_by_offerslink(coursevania.offers_link)
    print(coursevania.coupons)


