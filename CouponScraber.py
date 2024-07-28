from Modules.RealDiscount import RealDiscount


class CouponScraber:
    def __init__(self) -> None:
        # coupons will be a list of [title, course_coupon]
        self.coupon_datas =[]
    
    def scrab(self, from_day:str, to_day:str):
        real_discount =RealDiscount()
        real_discount.get_articles_link()
        real_discount.get_offerslink_by_articleslink(real_discount.articles_link[from_day:to_day])
        real_discount.collectcoupons_by_offerslink(real_discount.offers_link)

        self.coupon_datas =real_discount.coupons