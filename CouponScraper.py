from Modules.ProxyScraper import ProxyScraper
from Modules.RealDiscount import RealDiscount
from Modules.Courcevania import Coursevania
from Modules.Courson import Courson
import urllib3

urllib3.disable_warnings()

class CouponScraper:
    def __init__(self) -> None:
        # coupons will be a list of [title, course_coupon]
        self.coupon_datas =[]
    
    def combineUniqueLinks(self, coupon_datas:list):
        for coupon_data in coupon_datas:
            for data in self.coupon_datas:
                if data[1]==coupon_data[1]: break
            else: self.coupon_datas.append(coupon_data)

    def scrap(self, from_day:str, to_day:str):
        proxyScraper =ProxyScraper(test_url='https://courson.xyz/coupons', quite=True)
        proxyScraper.scrap()
        proxyScraper.splitGoodProxies()
        self.proxies =proxyScraper.good_proxies
        print("Working proxies:", len(self.proxies))

        # real discount
        real_discount =RealDiscount()
        real_discount.get_articles_link()
        real_discount.get_offerslink_by_articleslink(real_discount.articles_link[from_day:to_day])
        real_discount.collectcoupons_by_offerslink(real_discount.offers_link)
        self.coupon_datas =real_discount.coupons

        # coursevania
        try:
            coursevania =Coursevania()
            coursevania.get_home_page_offerslink(from_day, to_day)
            coursevania.get_coupons_by_offerslink(coursevania.offers_link)
            self.combineUniqueLinks(coursevania.coupons)
        except Exception as e:
            print("Coursevania offers cant fetch.")

        # courson
        courson =Courson(proxies=self.proxies, max_threads=2)
        courson.collect_course_pages()
        courson.collect_coupons_by_course_pages(courson.course_pages)
        self.combineUniqueLinks(courson.coupons)

