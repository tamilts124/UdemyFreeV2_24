import cloudscraper, requests
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread

requests =cloudscraper.CloudScraper()
# requests =cloudscraper.create_scraper()
class Courson:
	
	def __init__(self, from_day:int=1, to_day:int=1):
		self.from_day =from_day
		self.to_day =to_day
		self.base_url ='https://courson.xyz'
		self.coupons =[]

	def collect_coupons(self):
		while self.from_day <= self.to_day:
			json_data =requests.post(self.base_url+'/load-more-coupons', json={"filters":{},"offset":30*self.from_day-1}).json()
			items =json_data.get('coupons', [])
			for item in items:
				coupon =f'https://www.udemy.com/course/{item.get('id_name')}/?couponCode={item.get('coupon_code')}'
				self.coupons.append([item.get('title'), coupon])
			self.from_day +=1

				
			
if __name__ ==	'__main__':
	courson =Courson(1, 1)
	courson.collect_coupons()
	print(courson.coupons)
		