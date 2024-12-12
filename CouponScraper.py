from Modules.ProxyScraper import ProxyScraper
from Modules.RealDiscount import RealDiscount
from Modules.Courcevania import Coursevania
from Modules.YoFreeSamples import YoFreeSamples
from Modules.UdemyFreebies import UdemyFreebies
from Modules.DiscUdemy import DiscUdemy
from Modules.CourseJoiner import CourseJoiner
from Modules.InfoGnu import InfoGnu
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
        # proxyScraper =ProxyScraper(test_url='https://courson.xyz/coupons', quite=True)
        # proxyScraper.scrap()
        # proxyScraper.splitGoodProxies()
        # self.proxies =proxyScraper.good_proxies
        # print("Working proxies:", len(self.proxies))

        # real discount
        real_discount =RealDiscount()
        real_discount.get_articles_link()
        real_discount.get_offerslink_by_articleslink(real_discount.articles_link[from_day:to_day])
        real_discount.collectcoupons_by_offerslink(real_discount.offers_link)
        self.combineUniqueLinks(real_discount.coupons)

        # coursevania
        try:
            coursevania =Coursevania()
            coursevania.get_home_page_offerslink(from_day, to_day)
            coursevania.get_coupons_by_offerslink(coursevania.offers_link)
            self.combineUniqueLinks(coursevania.coupons)
        except Exception as e:
            print("Coursevania offers cant fetch. Error:", e)

        # yofreesamples
        try:
            yoFreeSamples =YoFreeSamples()
            yoFreeSamples.collect_coupons()
            self.combineUniqueLinks(yoFreeSamples.coupons)
        except Exception as e:
            print("YoFreeSamples offers cant fetch. Error:", e)

        # udemyfreebies
        try:
            udemyFreebies =UdemyFreebies(from_day+1, to_day)
            udemyFreebies.collect_freebies_course_links()
            udemyFreebies.collect_coupons(udemyFreebies.freebies_course_links)
            self.combineUniqueLinks(udemyFreebies.coupons)
        except Exception as e:
            print("Udemy Freebies offers cant fetch. Error:", e)


        # discudemy
        try:
            discUdemy =DiscUdemy(from_day+1, to_day)
            discUdemy.collect_discudemy_course_urls()
            discUdemy.collect_courses(discUdemy.discudemy_course_urls)
            self.combineUniqueLinks(discUdemy.coupons)
        except Exception as e:
            print("Disc Udemy offers cant fetch. Error:", e)

        # coursejoiner
        try:
            courseJoiner =CourseJoiner(from_day+1, to_day)
            courseJoiner.collect_course_joiner_coupon_links()
            courseJoiner.collect_courses(courseJoiner.course_joiner_coupon_links)
            self.combineUniqueLinks(courseJoiner.coupons)
        except Exception as e:
            print("Course Joiner offers cant fetch. Error:", e)

        # infognu
        try:
            infoGnu =InfoGnu(from_day+1, to_day)
            infoGnu.collect_infognu_course_urls()
            infoGnu.collect_courses(infoGnu.infognu_course_urls)
            self.combineUniqueLinks(infoGnu.coupons)
        except Exception as e:
            print("Info Gnu offers cant fetch. Error:", e)

        # # courson
        # courson =Courson(proxies=self.proxies, max_threads=2)
        # courson.collect_course_pages()
        # courson.collect_coupons_by_course_pages(courson.course_pages)
        # self.combineUniqueLinks(courson.coupons)

