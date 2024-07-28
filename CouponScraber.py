from Modules.RealDiscount import RealDiscount
from Modules.Courcevania import Coursevania

class CouponScraber:
    def __init__(self) -> None:
        # coupons will be a list of [title, course_coupon]
        self.coupon_datas =[]
    
    def combineUniqueLinks(self, coupon_datas:list):
        for coupon_data in coupon_datas:
            for data in self.coupon_datas:
                if data[1]==coupon_data[1]: break
            else: self.coupon_datas.append(coupon_data)

    def scrab(self, from_day:str, to_day:str):
        real_discount =RealDiscount()
        real_discount.get_articles_link()
        real_discount.get_offerslink_by_articleslink(real_discount.articles_link[from_day:to_day])
        real_discount.collectcoupons_by_offerslink(real_discount.offers_link)
        self.coupon_datas =real_discount.coupons

        # coursevania =Coursevania()
        # coursevania.get_home_page_offerslink(from_day, to_day)
        # coursevania.get_coupons_by_offerslink(coursevania.offers_link)
        # self.combineUniqueLinks(coursevania.coupons)

