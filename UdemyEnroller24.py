import os, json, pickle
from Modules.Udemy import Udemy
from CouponScraper import CouponScraper
from Modules.AES_Base64 import AES_Base64

SECURE_KEY =os.environ['SECURE_KEY']

EMAIL =os.environ['EMAIL']
PASSWORD =os.environ['PASSWORD']

ACCESSTOKEN =os.environ['ACCESS_TOKEN']
SESSIONID =os.environ['SESSION_ID']
MYACCESSTOKENS =list(filter(lambda s: bool(s), os.environ['MYACCESSTOKENS'].split(',')))

def main():
    key =SECURE_KEY.encode()
    cipher =AES_Base64(key)

    udemy =None

    if os.path.exists('encrypted_session.txt'):
        with open('encrypted_session.txt', 'rt') as file:
            file_data =file.read()
            if not file_data:
                print('Session data not found.')
            else:
                json_data =json.loads(file_data)

                nonse =json_data['nonse'].encode()
                tag =json_data['tag'].encode()
                encrypted_data =json_data['encrypted_data'].encode()

                data_base64 =cipher.decryptDataAES(encrypted_data, tag, nonse)
                pickle_data =cipher.decodeBase64(data_base64)

                udemy =pickle.loads(pickle_data)
                if udemy.check_login_alive():
                    print("Session Loaded.")
                else:
                    print("Session Expired.")
                    udemy =None

    if udemy==None:
        udemy =Udemy()
        if EMAIL and PASSWORD:
            udemy.login_with_credentials(EMAIL, PASSWORD)
        else:
            udemy.sessionid =SESSIONID
            udemy.accesstoken =ACCESSTOKEN

        udemy.myaccesstokens =MYACCESSTOKENS
    
    couponScraper =CouponScraper()
    couponScraper.scrap(0, 2)
    coupon_datas =couponScraper.coupon_datas

    udemy.check_coupon_and_addcart(coupon_datas)
    print(udemy.courses_cart, udemy.usable_coupons, udemy.nonusable_coupons)
    if len(udemy.usable_coupons)==0:
        print("No coupons Availbales to Enroll.")
    else:
        status =udemy.enroll_courses(udemy.courses_cart)
        print("Total Coupons:", len(udemy.usable_coupons))
        print("Entroll Status:","Success" if status else "Failed")
    
    if udemy.login==True:
        with open('encrypted_session.txt', 'wt') as file:
            pickle_data =pickle.dumps(udemy)
            bas64_data =cipher.encodeBase64(pickle_data)
            encrypted_data, tag, nonse =cipher.encryptDataAES(bas64_data)

            file_data ={
                "encrypted_data": encrypted_data.decode(),
                "tag": tag.decode(),
                "nonse": nonse.decode()
            }

            file.write(json.dumps(file_data))
        print("Session Updated.")



if __name__ == '__main__':
    main()