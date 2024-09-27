import cloudscraper, json, requests
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup


# requests =cloudscraper.CloudScraper()
class Udemy:
    def __init__(self, accesstoken:str='', sessionid:str='', myaccesstokens:list=[], max_threads:int=5) -> None:
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
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': r'https://www.udemy.com/join/login-popup/?locale=en_US&next=https%3A%2F%2Fwww.udemy.com%2F&response_type=html&response_type=json',
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
        course_title =coupon_data[0]
        course_name =coupon_data[1].split('/')[-2]
        coupon_code =coupon_data[1].split('=')[-1]
        course_id, result_json =None, None
        while True:
            try:
                if not course_id: course_id =self.get_courseid_by_course_pagedata(requests.get(coupon_data[1]).text)
                if not result_json: result_json =self.get_coupon_status(course_id, coupon_code)
                if course_id: break
            except Exception as e:
                print(e, 'Udemy Prevention Detected.', )
                pass
        if result_json and result_json.get('uses_remaining', ''):
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
                Thread(target=self.thread_check_coupon_and_addcart, args=[coupon_datas[coupon_data_index]]).start()
                self.threads +=1
            while (self.threads>=self.max_threads or (coupon_data_index==len(coupon_datas)-1 and len(coupon_datas)>len(self.usable_coupons)+len(self.nonusable_coupons))):
                # print(f'{len(self.usable_coupons)+len(self.nonusable_coupons)}/{len(coupon_datas)}', '\r')
                sleep(0.2)
        # print(f'{len(self.usable_coupons)+len(self.nonusable_coupons)}/{len(coupon_datas)}', '\r')

    def enroll_courses(self, courses_cart:list):
        try:
            common_data ={
                "checkout_environment":"Marketplace",
                "checkout_event":"Submit",
                "shopping_info":{"items":courses_cart,"is_cart":False},
                "payment_info":{"method_id":"0","payment_vendor":"Free","payment_method":"free-method"}
            }
            # if os.environ.get('CF_CLEARANCE'): cookies['cf_clearance'] =os.environ['CF_CLEARANCE']
            result_page =requests.post('https://www.udemy.com/payment/checkout-submit/', headers={'Content-Type': 'application/json'}, cookies=self.cookies, data=json.dumps(common_data))
            result_json =result_page.json()
            # print(result_json, common_data)
            if result_json.get('status', '')=='succeeded': return True
            elif 'You do not have permission to perform this action' in result_json.get('detail', ''):
                    raise Exception('Enroll Fail, Session id or Access Token is Expired...\n')
        except (Exception, json.JSONDecodeError) as e:
            if result_page.status_code==504:return True
            else: print(e)
        return False

    def login_with_credentials(self, email:str, password:str):
        session =requests.Session()
        session.headers =self.headers
        session.get(r'https://www.udemy.com/join/login-popup/?locale=en_US&next=https%3A%2F%2Fwww.udemy.com%2F&response_type=html&response_type=json')
        
        if session.cookies.get('csrftoken') == None:
            raise Exception('CSRF Token fetch error. Cloudflare blocked the request.')
        sleep(3)

        files =[('email', (None, email)), ('password', (None, password)), ('csrfmiddlewaretoken', (None, session.cookies.get('csrftoken')))]
        login_result =session.post(r'https://www.udemy.com/join/login-popup/?locale=en_US&next=https%3A%2F%2Fwww.udemy.com%2F&response_type=html&response_type=json', files=files)
        
        if 'formErrors' in login_result.text:
            raise Exception(login_result.text)
        else:
            self.accesstoken =session.cookies.get('access_token', '')
            self.sessionid =session.cookies.get('dj_session_id', '')
        
        if self.accesstoken=='' or self.sessionid=='':
            raise Exception('IMPORTANT: Udemy preventing to login.')

        self.login =True
        sleep(3)
        
        user_header =session.get('https://www.udemy.com/api-2.0/contexts/me/?header=true').json()
        self.log_out_url =user_header.get('header').get('user').get('logout_url')
        
        self.login_session =session
        print("Login success.\n")

    def logout(self):
        res =self.login_session.get(r'https://www.udemy.com'+self.log_out_url)

        self.accesstoken =''
        self.sessionid =''

        print('Logout success.')

    def check_login_alive(self):
        user_header =self.login_session.get('https://www.udemy.com/api-2.0/contexts/me/?header=true').json()
        return bool(user_header.get('header').get('isLoggedIn'))


if __name__ == '__main__':
    udemy =Udemy()
    udemy.login_with_credentials("email", "password")
    udemy.logout()


