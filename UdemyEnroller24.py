import os, json, pickle, math
from Modules.Udemy import Udemy
from CouponScraper import CouponScraper
from Modules.AES_Base64 import AES_Base64

# SECURE_KEY =os.environ['SECURE_KEY']

# EMAIL =os.environ['EMAIL']
# PASSWORD =os.environ['PASSWORD']
# GMAIL_APP_PASSWORD =os.environ['GMAIL_APP_PASSWORD']

# ACCESSTOKEN =os.environ['ACCESS_TOKEN']
# SESSIONID =os.environ['SESSION_ID']
# MYACCESSTOKENS =list(filter(lambda s: bool(s), os.environ['MYACCESSTOKENS'].split(',')))


def main():
    # key =SECURE_KEY.encode()
    # cipher =AES_Base64(key)

    udemy =None

    # if os.path.exists('encrypted_session.txt'):
    #     with open('encrypted_session.txt', 'rt') as file:
    #         file_data =file.read()
    #         if not file_data:
    #             print('Session data not found.')
    #         else:
    #             json_data =json.loads(file_data)

    #             nonse =json_data['nonse'].encode()
    #             tag =json_data['tag'].encode()
    #             encrypted_data =json_data['encrypted_data'].encode()

    #             data_base64 =cipher.decryptDataAES(encrypted_data, tag, nonse)
    #             pickle_data =cipher.decodeBase64(data_base64)

    #             udemy =pickle.loads(pickle_data)
    #             if udemy.check_login_alive():
    #                 print("Session Loaded.")
    #             else:
    #                 print("Session Expired.")
    #                 udemy =None

    # couponScraper =CouponScraper()
    # couponScraper.scrap(0, 2)
    # coupon_datas =couponScraper.coupon_datas

    # if udemy==None:
    #     udemy =Udemy()
    #     if EMAIL and PASSWORD:
    #         udemy.login_with_credentials(EMAIL, PASSWORD, GMAIL_APP_PASSWORD)
    #     else:
    #         udemy.sessionid =SESSIONID
    #         udemy.accesstoken =ACCESSTOKEN

    #     udemy.myaccesstokens =MYACCESSTOKENS

    udemy =Udemy('"YxVao1u6eFJ4lVAm5Y/fPegLykR8tXuPaVAaJ3yZTsE:Edzmbn85Ank9BR2D75GeCPafDZEW3UQId0wsbNo9CMc"', 'yc565u8asprby0iv9ym2vxu8r5a975ou')
    
    udemy.courses_cart =[]
    udemy.usable_coupons =[]
    udemy.nonusable_coupons =[]

    # test =[['Discover Proven and Rapid Money-Making Strategies', 'https://www.udemy.com/course/discover-proven-and-rapid-money-making-strategies/'], ['Content Marketing: Blog to Business Success', 'https://www.udemy.com/course/content-marketing-blog-to-business-success/?couponCode=JOZISTYLEUDEMY'], ['Altman Z-Score: Measuring Company Strength and Risk', 'https://www.udemy.com/course/altman-z-score-measuring-company-strength-and-risk/?couponCode=ALTMAN'], ['Creating a Stylized House and Props in Blender 2025', 'https://www.udemy.com/course/creating-a-stylized-house-and-props-in-blender/?couponCode=CP130525'], ['Using AI To Code Machine Learning Apps', 'https://www.udemy.com/course/using-ai-to-code-machine-learning-apps/'], ['Microsoft Excel – Beginners Introduction to Excel (Volume 3)', 'https://www.udemy.com/course/microsoft-excel-beginners-introduction-to-excel-volume-3/'], ['An Introduction to Aruba Networking Solutions – Part 1', 'https://www.udemy.com/course/an-introduction-to-aruba-networking-solutions-part-1/'], ['Master Python and Ace the PCAP-31-03 Certification', 'https://www.udemy.com/course/master-python-and-ace-the-pcap-31-03-certification/?couponCode=2BC8B291EE4194A27BEF'], ['Learn Python Programming for Ultimate Beginners', 'https://www.udemy.com/course/pythoncoding/'], ['The Beginner’s Guide to Bash Scripting and Automation', 'https://www.udemy.com/course/the-beginners-guide-to-bash-scripting-and-automation/?couponCode=EECC2B075052DD3EC9B7'], ['Learn the basics of how to negotiate well in work and life', 'https://www.udemy.com/course/learn-the-basics-of-how-to-negotiate-well-in-work-and-life/'], ['Data Analysis with Excel and Power BI', 'https://www.udemy.com/course/dataanalysiswithexcelandpbi/']]

    test =[['Content Marketing: Blog to Business Success', 'https://www.udemy.com/course/content-marketing-blog-to-business-success/?couponCode=JOZISTYLEUDEMY'], ['Altman Z-Score: Measuring Company Strength and Risk', 'https://www.udemy.com/course/altman-z-score-measuring-company-strength-and-risk/?couponCode=ALTMAN'], ['Master Python and Ace the PCAP-31-03 Certification', 'https://www.udemy.com/course/master-python-and-ace-the-pcap-31-03-certification/?couponCode=2BC8B291EE4194A27BEF']]

    test =[test[1]]

    udemy.check_coupon_and_addcart(test)
    # udemy.check_coupon_and_addcart(coupon_datas)
    print(udemy.courses_cart, udemy.usable_coupons, udemy.nonusable_coupons)



    if len(udemy.usable_coupons)==0:
        print("No coupons Availbales to Enroll.")
    else:
        udemy_enroll_limit =30
        for i in range(math.ceil(len(udemy.courses_cart)/udemy_enroll_limit)):
            status =udemy.enroll_courses(udemy.courses_cart[i*udemy_enroll_limit:(i+1)*udemy_enroll_limit])
            print("Working Coupons:", len(udemy.usable_coupons))
            print("Wasted Coupons:", len(udemy.nonusable_coupons))
            print("Enroll Coupons:", len(udemy.courses_cart[i*udemy_enroll_limit:(i+1)*udemy_enroll_limit]))
            print("Entroll Status:","Success" if status else "Failed")
            print()

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