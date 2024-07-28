import requests
from bs4 import BeautifulSoup
from threading import Thread
from time import sleep

class RealDiscount:

    def __init__(self, max_threads:int=5) -> None:
        self.max_threads =max_threads
        self.threads =0
        # articles
        self.articles_link =[]
        self.offers_link =[]
        # final coupons
        self.coupons =[]
        self.wastes =[]

    def get_articles_link(self):
        anger_tags =BeautifulSoup(requests.get('https://www.real.discount/articles/').text, 'html.parser').findAll('a')
        for anger_tag in anger_tags:
            if anger_tag.get('href', '').startswith('https://app.real.discount/article/'): self.articles_link.append(anger_tag['href'])
        
    def get_offerslink_by_articleslink(self, articles_link:list):
        self.offers_link =[]
        for article in articles_link:
            while True:
                page =requests.get(article)
                if page.status_code<500: break
                print("Real discount Prevention detected.")
            div_tags =BeautifulSoup(page.text, 'html.parser').findAll('div', {'class':'ml-3'})
            for div_tag in div_tags:
                sub_div_tags =div_tag.findAll('div')
                if sub_div_tags[1].find('span', {'class':'text-muted text-sm ml-2'}).string.split(' ')[-1]=='0$' and sub_div_tags[0].a['href'].startswith('/offer/'):
                    self.offers_link.append((sub_div_tags[0].a['href'], sub_div_tags[0].a.string))

    def thread_collectoffer(self, offer:tuple):
        result_page =requests.get(f'https://www.real.discount{offer[0]}').text
        self.threads -=1
        links =BeautifulSoup(result_page, 'html.parser').findAll('a')
        for link in links:
            if 'https://www.udemy.com/course/' in link.get('href', ''):
                self.coupons.append([offer[1], link['href'].split('murl=')[-1]])
                break
        else: self.wastes.append(offer[1])

    def collectcoupons_by_offerslink(self, offers_link:list):
        self.threads =0
        offers_link =offers_link[0:5]
        for offer in range(len(offers_link)):
            Thread(target=self.thread_collectoffer, args=[offers_link[offer]]).start()
            self.threads +=1
            while (self.threads>=self.max_threads or (offer==len(offers_link)-1 and len(offers_link)>len(self.coupons)+len(self.wastes))):
                # print(f'{len(self.coupons)+len(self.wastes)}/{len(offers_link)}', '\r')
                sleep(0.2)        
        # print(f'{len(self.coupons)+len(self.wastes)}/{len(offers_link)}', '\r')
        
if __name__ == '__main__':
    real_discount =RealDiscount()
    real_discount.get_articles_link()
    real_discount.get_offerslink_by_articleslink(real_discount.articles_link[0:1])
    real_discount.collectcoupons_by_offerslink(real_discount.offers_link)

    print(real_discount.coupons)
    print(real_discount.wastes)