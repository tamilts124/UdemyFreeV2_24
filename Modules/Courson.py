import cloudscraper, requests
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread

requests =cloudscraper.CloudScraper()
# requests =cloudscraper.create_scraper()
class Courson:
	
	def __init__(self, proxies:list=[], max_threads:int=10):
		self.host ='https://courson.xyz'
		self.course_pages =[]
		self.coupons =[]

		self.proxies =proxies
		self.proxy_index =0
		self.proxy_mindex =len(proxies)
		self.change_proxy()
		self.timeout =10

		self.threads =0
		self.max_threads =max_threads

	def change_proxy(self):	
		self.proxy_mindex =len(self.proxies)
		if self.proxy_index>=self.proxy_mindex:
			self.proxy_index =0
		if self.proxy_mindex:
			print(self.proxy_index, self.proxy_mindex)
			self.proxy =self.proxies[self.proxy_index]
			self.proxy_index +=1
		else: self.proxy =None

	def collect_course_pages(self):
		global requests
		while True:
			try:
				courson_page =requests.get('https://courson.xyz/coupons', proxies=self.proxy, timeout=self.timeout)
			except Exception as e:
				print("Proxy timeout:", self.proxy)
				self.proxies =list(filter(lambda e: e!=self.proxy, self.proxies))
				self.change_proxy()
				continue
			if courson_page.status_code==200: break
			# print(courson_page.status_code, 1, self.proxy)
			requests =cloudscraper.CloudScraper()
			if courson_page.status_code==403:
				continue
			else: sleep(self.timeout)
			self.change_proxy()
			
		courson_soup =BeautifulSoup(courson_page.text, 'html.parser')
		
		all_course_cards =courson_soup.findAll('a', {'class': 'course-preview-link'})
		
		for card in all_course_cards:
			link =self.host+card['href']
			title =card.find('h6', {'class': 'preview-title'}).text
			self.course_pages.append([title, link])
			
	def collect_coupon_by_course_page(self, course_page:list=[], proxy:dict={}):
		global requests
		while True:
			try:
				course =requests.get(course_page[1], proxies=proxy, timeout=self.timeout)
			except Exception as e:
				print("Proxy timeout:", proxy)
				self.proxies =list(filter(lambda e: e!=proxy, self.proxies))
				self.change_proxy()
				proxy =self.proxy
				continue
			if course.status_code==200: break
			# print(course.status_code)
			requests =cloudscraper.CloudScraper()
			if course.status_code==403:
				continue
			else: sleep(self.timeout)
			self.change_proxy()
			proxy =self.proxy

		page_soup =BeautifulSoup(course.text, 'html.parser')
		enroll_button =page_soup.find('div', {'class':'enroll-btn'})
		coupon_link =enroll_button.find('a')['href']
		self.coupons.append([course_page[0], coupon_link])
		self.threads -=1

	def collect_coupons_by_course_pages(self, course_pages:list=[]):
		for index, course_page in enumerate(course_pages):
			self.threads +=1
			Thread(target=self.collect_coupon_by_course_page, args=[course_page, self.proxy]).start()
			while self.threads >= self.max_threads or (index==len(course_pages)-1 and len(self.coupons)<len(course_pages)):
				# print(f'{len(self.coupons)}/{len(course_pages)}')
				sleep(0.5)
				
			
if __name__ ==	'__main__':
	courson =Courson(max_threads=2)
	courson.collect_course_pages()
	courson.collect_coupons_by_course_pages(courson.course_pages)
	print(courson.coupons)
		