import requests
from threading import Thread
from time import sleep
import urllib3

urllib3.disable_warnings()

class ProxyScraper:

    def __init__(self, test_url:str='https://www.google.com/', max_threads:int=20, quite:bool=False):
        self.proxies=[]
        self.good_proxies=[]
        self.bad_proxies=[]
        # 10 seconds
        self.validatePeriod =3
        self.test_url =test_url
        self.threads =0
        self.max_threads =10
        self.quite =quite

    def scrap(self):
        try:
            proxies =requests.get('https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc').json()
            proxies =proxies['data']
            self.proxies =list(map(lambda e: {'http': f'{e["protocols"][0]}://{e["ip"]}:{e["port"]}/', 'https': f'{e["protocols"][0]}://{e["ip"]}:{e["port"]}/'}, proxies))
        except Exception: print("Proxies fetch error.")

    def proxyTest(self, proxy:dict):
        try:
            requests.get(self.test_url, proxies=proxy, timeout=self.validatePeriod)
            self.good_proxies.append(proxy)
        except Exception: self.bad_proxies.append(proxy)
        self.threads -=1

    def splitGoodProxies(self):
        for proxy in range(len(self.proxies)):
            Thread(target=self.proxyTest, args=[self.proxies[proxy]]).start()
            self.threads +=1
            while self.threads>=self.max_threads or proxy==len(self.proxies)-1 and len(self.good_proxies)+len(self.bad_proxies)<len(self.proxies):
                if self.quite==False: print(f"{len(self.good_proxies)} {len(self.bad_proxies)}/{len(self.proxies)}", '\r')
                sleep(0.5)

if __name__ == '__main__':
    proxyScraper =ProxyScraper(test_url='https://courson.xyz/coupons')
    proxyScraper.scrap()    
    # print(proxyScraper.proxies)
    proxyScraper.splitGoodProxies()
    print(proxyScraper.good_proxies)