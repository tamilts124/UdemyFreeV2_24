from Modules.ProxyScraper import ProxyScraper
from Modules.RealDiscount import RealDiscount
from Modules.Courcevania import Coursevania
from Modules.YoFreeSamples import YoFreeSamples
from Modules.UdemyFreebies import UdemyFreebies
from Modules.DiscUdemy import DiscUdemy
from Modules.CourseJoiner import CourseJoiner
from Modules.InfoGnu import InfoGnu
from Modules.CouponScorpion import CouponScorpion
from Modules.Courson import Courson
from Modules.OnlineCourses import OnlineCourses
from Modules.CourseCouponClub import CourseCouponClub
from Modules.ScrollCoupons import ScrollCoupons
from Modules.OnlineTutorials import OnlineTutorials
from Modules.CursosDev import CursosDev
from Modules.CouponsEagle import CouponsEagle
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
        try:
            realDiscount =RealDiscount(from_day+1, to_day)
            realDiscount.collect_coupons()
            print('Real Discount:', len(realDiscount.coupons))
            self.combineUniqueLinks(realDiscount.coupons)
        except Exception as e:
            print("Real discount offers cant fetch. Error:", e)

        # coursevania
        try:
            coursevania =Coursevania()
            coursevania.get_home_page_offerslink(from_day, to_day)
            coursevania.get_coupons_by_offerslink(coursevania.offers_link)
            print('Coursevania:', len(coursevania.coupons))
            self.combineUniqueLinks(coursevania.coupons)
        except Exception as e:
            print("Coursevania offers cant fetch. Error:", e)

        # yofreesamples
        try:
            yoFreeSamples =YoFreeSamples()
            yoFreeSamples.collect_coupons()
            print('YoFreeSamples:', len(yoFreeSamples.coupons))
            self.combineUniqueLinks(yoFreeSamples.coupons)
        except Exception as e:
            print("YoFreeSamples offers cant fetch. Error:", e)

        # udemyfreebies
        try:
            udemyFreebies =UdemyFreebies(from_day+1, to_day)
            udemyFreebies.collect_freebies_course_links()
            udemyFreebies.collect_coupons(udemyFreebies.freebies_course_links)
            print('Udemy Freebies:', len(udemyFreebies.coupons))
            self.combineUniqueLinks(udemyFreebies.coupons)
        except Exception as e:
            print("Udemy Freebies offers cant fetch. Error:", e)


        # discudemy
        try:
            discUdemy =DiscUdemy(from_day+1, to_day)
            discUdemy.collect_discudemy_course_urls()
            discUdemy.collect_courses(discUdemy.discudemy_course_urls)
            print('Disc Udemy:', len(discUdemy.coupons))
            self.combineUniqueLinks(discUdemy.coupons)
        except Exception as e:
            print("Disc Udemy offers cant fetch. Error:", e)

        # coursejoiner
        try:
            courseJoiner =CourseJoiner(from_day+1, to_day)
            courseJoiner.collect_course_joiner_coupon_links()
            courseJoiner.collect_courses(courseJoiner.course_joiner_coupon_links)
            print('Course Joiner:', len(courseJoiner.coupons))
            self.combineUniqueLinks(courseJoiner.coupons)
        except Exception as e:
            print("Course Joiner offers cant fetch. Error:", e)

        # infognu
        try:
            infoGnu =InfoGnu(from_day+1, to_day)
            infoGnu.collect_infognu_course_urls()
            infoGnu.collect_courses(infoGnu.infognu_course_urls)
            print('Info Gnu:', len(infoGnu.coupons))
            self.combineUniqueLinks(infoGnu.coupons)
        except Exception as e:
            print("Info Gnu offers cant fetch. Error:", e)

        # coupon scorpion
        try:
            couponScorpion =CouponScorpion(from_day+1, to_day)
            couponScorpion.collect_couponscorpion_course_urls()
            couponScorpion.collect_courses(couponScorpion.couponscorpion_course_urls)
            print('Coupon Scorpion:', len(couponScorpion.coupons))
            self.combineUniqueLinks(couponScorpion.coupons)
        except Exception as e:
            print("Coupon Scorpion offers cant fetch. Error:", e)

        # onlinecourses
        try:
            onlineCourses =OnlineCourses(from_day+1, to_day)
            onlineCourses.collect_onlinecourses_course_urls()
            onlineCourses.collect_courses(onlineCourses.onlinecourses_course_urls)
            print('Online Courses:', len(onlineCourses.coupons))
            self.combineUniqueLinks(onlineCourses.coupons)
        except Exception as e:
            print("Online Courses offers cant fetch. Error:", e)


        # course coupon club
        try:
            courseCouponClub =CourseCouponClub(from_day+1, to_day)
            courseCouponClub.collect_coursecouponclub_course_urls()
            courseCouponClub.collect_courses(courseCouponClub.coursecouponclub_course_urls)
            print('Course Coupon Club:', len(courseCouponClub.coupons))
            self.combineUniqueLinks(courseCouponClub.coupons)
        except Exception as e:
            print("Course Coupon Club offers cant fetch. Error:", e)

        # scroll coupons
        try:
            scrollCoupons =ScrollCoupons(from_day+1, to_day)
            scrollCoupons.collect_scrollcoupons_course_urls()
            scrollCoupons.collect_courses(scrollCoupons.scrollcoupons_course_urls)
            print('Scroll Coupons:', len(scrollCoupons.coupons))
            self.combineUniqueLinks(scrollCoupons.coupons)
        except Exception as e:
            print("Scroll Coupons offers cant fetch. Error:", e)

        # online tutorials
        try:
            onlineTutorials =OnlineTutorials(from_day+1, to_day)
            onlineTutorials.collect_onlinetutorials_course_urls()
            onlineTutorials.collect_courses(onlineTutorials.onlinetutorials_course_urls)
            print('Online Tutorials:', len(onlineTutorials.coupons))
            self.combineUniqueLinks(onlineTutorials.coupons)
        except Exception as e:
            print("Online Tutorials offers cant fetch. Error:", e)

        # Cursos Dev
        try:
            cursosDev =CursosDev(from_day+1, to_day)
            cursosDev.collect_cursosdev_course_urls()
            cursosDev.collect_courses(cursosDev.cursosdev_course_urls)
            print('Cursos Dev:', len(cursosDev.coupons))
            self.combineUniqueLinks(cursosDev.coupons)
        except Exception as e:
            print("Cursos Dev offers cant fetch. Error:", e)

        # Coupons Eagle
        try:
            couponsEagle =CouponsEagle(from_day+1, to_day)
            couponsEagle.collect_couponseagle_course_urls()
            couponsEagle.collect_courses(couponsEagle.couponseagle_course_urls)
            print('Coupons Eagle:', len(couponsEagle.coupons))
            self.combineUniqueLinks(couponsEagle.coupons)
        except Exception as e:
            print("Coupons Eagle offers cant fetch. Error:", e)

        # Courson
        try:
            courson =Courson(from_day+1, to_day)
            courson.collect_coupons()
            print('Courson:', len(courson.coupons))
            self.combineUniqueLinks(courson.coupons)
        except Exception as e:
            print("Courson offers cant fetch. Error:", e)

        print('\n')



