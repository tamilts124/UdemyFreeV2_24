import os
from Modules.Udemy import Udemy
from CouponScraper import CouponScraper

ACCESSTOKEN =os.environ['ACCESS_TOKEN']
SESSIONID =os.environ['SESSION_ID']
CFCLEARANCE =os.environ['CF_CLEARANCE']

MYACCESSTOKENS =list(filter(lambda s: bool(s), os.environ['MYACCESSTOKENS'].split(',')))

def main():
    udemy =Udemy(ACCESSTOKEN, SESSIONID, CFCLEARANCE, MYACCESSTOKENS)
    couponScraber =CouponScraber()
    couponScraber.scrab(0, 1)
    coupon_datas =couponScraber.coupon_datas

    # print(coupon_datas[0:5])

    # coupon_datas =[['JavaScript OOP: Mastering Modern Object-Oriented Programming', 'https://www.udemy.com/course/javascript-oop-mastering-modern-object-oriented-programming/?couponCode=9EFF95C70CB02E15E371'],
    # ['PHP Laravel 2023: Build Food Ordering Ecommerce Store', 'https://www.udemy.com/course/php-laravel-2023-build-food-ordering-ecommerce-store/?couponCode=LARAVELFOOD48'],
    # ['Learn HTML and CSS from Beginning to Advanced', 'https://www.udemy.com/course/learn-html-and-css-from-beginning-to-advanced/?couponCode=F18356CBAAD81EF70B77'],
    # ['CSS Fundamentals: Comprehensive Training for Web Developers', 'https://www.udemy.com/course/css-fundamentals-comprehensive-training-for-web-developers/?couponCode=2DEFCB0D4FC6CE16FFD3'],
    # ['Mastering C & C++ Programming: From Fundamentals to Advanced', 'https://www.udemy.com/course/mastering-c-c-plus-programming-from-fundamentals-to-advanced/?couponCode=CCF0646E172B71BF0472']]
    # print(coupon_datas)
    udemy.check_coupon_and_addcart(coupon_datas)
    # print(udemy.courses_cart, udemy.usable_coupons, udemy.nonusable_coupons)
    if len(udemy.usable_coupons)==0:
        print("No coupons Availbales to Enroll.")
    else:
        status =udemy.enroll_courses(udemy.courses_cart)
        print("Entroll Status:","Success" if status else "Failed" )

if __name__ == '__main__':
    main()