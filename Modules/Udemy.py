import cloudscraper, json, requests
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup
from Modules.UdemyChromeLogin import launch_udemy_login, submit_otp
from Modules.EmailReader import EmailReader
from datetime import datetime, timezone
import re

# requests =cloudscraper.CloudScraper()
class Udemy:
    def __init__(self, accesstoken:str='', sessionid:str='', myaccesstokens:list=[], max_threads:int=50) -> None:
        self.max_threads =max_threads
        self.threads =0

        self.accesstoken =accesstoken
        self.sessionid =sessionid
        self.cookies={'access_token': self.accesstoken, 'dj_session_id': self.sessionid}
        # other udemy accounts access token
        self.myaccesstokens =myaccesstokens
        # freely buyable course cart list
        self.courses_cart =[]


        # temp_variables
        self.usable_coupons =[]
        self.nonusable_coupons =[]

        # old coupons
        self.known_coupons =[]

        # login and logout
        self.headers ={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Referer': r'https://www.udemy.com/join/login-popup/?locale=en_US&next=https%3A%2F%2Fwww.udemy.com%2F&response_type=html&response_type=json',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        self.login =False
        self.log_out_url =''

        # login session
        self.login_session =''

    def get_courseid_by_course_pagedata(self, page_data:str):
        datas =page_data.split('https://img-c.udemycdn.com/course/')
        for data in datas:
            if '.jpg' in data:
                datas =data.split('/')
                for data in datas:
                    if '.jpg' in data:
                        datas =data.split('\\')
                        for data in datas:
                            if '.jpg' in data:
                                datas =data.split('_')
                                return int(datas[0])
    
    def get_coupon_status(self, course_id:int, coupon:str):
        json_data =requests.get(f'https://www.udemy.com/api-2.0/course-landing-components/{course_id}/me/?components=purchase,redeem_coupon,discount_expiration&discountCode={coupon}')
        json_data =json_data.json()
        if not json_data.get('redeem_coupon'): return
        status =json_data['redeem_coupon']['discount_attempts'][0]['status']
        if status=='applied':return {
            'uses_remaining':json_data['purchase']['data']['pricing_result']['campaign']['uses_remaining'],
            'real_price':json_data['purchase']['data']['pricing_result']['list_price']['amount'],
            'end_time':[json_data['discount_expiration']['data']['discount_deadline_text'] if json_data.get('discount_expiration') else ''][0]
        }
    
    def thread_check_coupon_and_addcart(self, coupon_data:list):
        self.cookies={'access_token': self.accesstoken, 'dj_session_id': self.sessionid}
        course_title =coupon_data[0]
        course_name =coupon_data[1].split('/')[-2]
        coupon_code =coupon_data[1].split('=')[-1]
        course_id, result_json, tries =None, None, 10
        while True:
            try:
                course_page =requests.get(coupon_data[1])
                if not course_id: course_id =self.get_courseid_by_course_pagedata(course_page.text)
                if not result_json: result_json =self.get_coupon_status(course_id, coupon_code)
                if course_id: break
                tries -=1
                # this course no longer allowed to enroll means, should break
                if course_page.status_code==302 or tries<=0: break
            except Exception as e:
                print(e, 'Udemy Prevention Detected.', )
                pass
        if result_json and result_json.get('uses_remaining', ''):
            # print('remaining uses:', result_json.get('uses_remaining', ''))
            while True:
                result_page =requests.get(f'https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/', cookies=self.cookies)
                if result_page.status_code<500: break
            if 'you do not have permission to perform this action.' in result_page.text.lower():
                # print(course_id, result_page.text, result_page.status_code)
                coupon_availablity =True
                for accesstoken in self.myaccesstokens:
                    while True:
                        result_page =requests.get(f'https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/', cookies={**self.cookies, 'access_token': accesstoken})
                        if result_page.status_code<500: break
                    if 'you do not have permission to perform this action.' not in result_page.text.lower():
                        coupon_availablity =False
                        break
                if coupon_availablity:
                    self.courses_cart.append({
                            "discountInfo":{"code":coupon_code},
                            "price":{"amount":0,"currency":"INR"},
                            "buyable":{"id":course_id,"type":"course"}
                    })
                    self.usable_coupons.append(coupon_data)
                else: self.nonusable_coupons.append(coupon_data)
            else: self.nonusable_coupons.append(coupon_data)
        else: self.nonusable_coupons.append(coupon_data)
        self.threads -=1

    def check_coupon_and_addcart(self, coupon_datas:list):
        self.threads =0
        for coupon_data_index in range(len(coupon_datas)):
            if coupon_datas[coupon_data_index][1] in self.known_coupons:
                self.nonusable_coupons.append(coupon_datas[coupon_data_index])
                continue
            else:
                self.threads +=1
                Thread(target=self.thread_check_coupon_and_addcart, args=[coupon_datas[coupon_data_index]]).start()
            while (self.threads>=self.max_threads or (coupon_data_index==len(coupon_datas)-1 and len(coupon_datas)>len(self.usable_coupons)+len(self.nonusable_coupons))):
                # print(f'{len(self.usable_coupons)+len(self.nonusable_coupons)}/{len(coupon_datas)}', '\r')
                sleep(0.2)
        # print(f'{len(self.usable_coupons)+len(self.nonusable_coupons)}/{len(coupon_datas)}', '\r')

    def enroll_courses(self, courses_cart:list):
        try:
            self.cookies={'access_token': self.accesstoken, 'dj_session_id': self.sessionid}

            common_data ={
                "checkout_environment":"Marketplace",
                "checkout_event":"Submit",
                "shopping_info":{"items":courses_cart,"is_cart":False},
                "payment_info":{"method_id":"0","payment_vendor":"Free","payment_method":"free-method"}
            }
            # if os.environ.get('CF_CLEARANCE'): cookies['cf_clearance'] =os.environ['CF_CLEARANCE']
            result_page =requests.post('https://www.udemy.com/payment/checkout-submit/', headers={'Content-Type': 'application/json'}, cookies=self.cookies, data=json.dumps(common_data))
            result_json =result_page.json()            

            # print(result_json)
            if result_json.get('status', '')=='succeeded': return True
            elif 'You do not have permission to perform this action' in result_json.get('detail', ''):
                    raise Exception('Enroll Fail, Session id or Access Token is Expired...\n')
        except (Exception, json.JSONDecodeError) as e:
            if result_page.status_code==504:return True
            else: print(e)
        return False

    def login_with_credentials(self, email:str, udemy_password:str, gmail_password:str):

        print('IMPORTANT: Launching Udemy automated login in chrome.')
        isOldLogin, browser_cookies =launch_udemy_login(email, udemy_password)
        if not isOldLogin:
            email_reader =EmailReader(email, gmail_password)
            email_reader.connect()
            mail =email_reader.filter_emails_combined(sender_email='no-reply@e.udemymail.com', subject_keyword='login', date=datetime.now(timezone.utc).strftime(r'%Y-%m-%d'), mailbox='[Gmail]/Spam', limit=1)
            if mail:
                mail_body =mail[0]['body']
                pattern = r"(\d{6})This code expires"
                match = re.search(pattern, mail_body)

                if match:
                    extracted_code = match.group(1)
                    browser_cookies =submit_otp(extracted_code)
                # print(cookies)
                
                else:
                    raise Exception('ERROR: OTP cant able to find.')
            else:
                raise Exception('ERROR: Unable to find the mail.')
        
        cookies ={}
        for cookie in browser_cookies:
            cookies[cookie['name']] =cookie['value']

        self.accesstoken =cookies.get('access_token', '')
        self.sessionid =cookies.get('dj_session_id', '')

        if not self.accesstoken or not self.sessionid:
            raise Exception('IMPORTANT: Udemy browser login failed.')

        self.cookies =cookies
        
        self.login =True
        sleep(3)
        
        user_header =requests.get('https://www.udemy.com/api-2.0/contexts/me/?header=true', cookies=self.cookies)
        # print(user_header.text); exit()
        self.log_out_url =user_header.json().get('header').get('user').get('logout_url')
        
        print("Login success.\n")

    def logout(self):
        res =requests.get(r'https://www.udemy.com'+self.log_out_url, cookies=self.cookies)

        self.accesstoken =''
        self.sessionid =''

        print('Logout success.')

    def check_login_alive(self):
        user_header =requests.get('https://www.udemy.com/api-2.0/contexts/me/?header=true', cookies=self.cookies).json()
        return bool(user_header.get('header').get('isLoggedIn'))


if __name__ == '__main__':
    udemy =Udemy()
    udemy.login_with_credentials("email", "password", "app_password")
    udemy.logout()