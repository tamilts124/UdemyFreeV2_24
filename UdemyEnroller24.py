import os
from Modules.Udemy import Udemy
from CouponScraper import CouponScraper

ACCESSTOKEN =os.environ['ACCESS_TOKEN']
SESSIONID =os.environ['SESSION_ID']
MYACCESSTOKENS =list(filter(lambda s: bool(s), os.environ['MYACCESSTOKENS'].split(',')))

# ACCESSTOKEN =''
# SESSIONID =''
# MYACCESSTOKENS =''

def main():
    udemy =Udemy(ACCESSTOKEN, SESSIONID, MYACCESSTOKENS)
    couponScraper =CouponScraper()
    couponScraper.scrap(0, 2)
    coupon_datas =couponScraper.coupon_datas

    udemy.check_coupon_and_addcart(coupon_datas)
    # print(udemy.courses_cart, udemy.usable_coupons, udemy.nonusable_coupons)
    if len(udemy.usable_coupons)==0:
        print("No coupons Availbales to Enroll.")
    else:
        status =udemy.enroll_courses(udemy.courses_cart)
        print("Total Coupons:", len(udemy.usable_coupons))
        print("Entroll Status:","Success" if status else "Failed" )

if __name__ == '__main__':
    main()