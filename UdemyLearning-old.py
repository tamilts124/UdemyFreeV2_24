from time import sleep
from threading import Thread
from bs4 import BeautifulSoup
import datetime as dt
import requests, json, os, urllib3

urllib3.disable_warnings()

class Realdiscount:

    def __init__(self, accesstoken, sessionid, ignore_accounts, fromday=0, today=1, requests_limit=10, enrolls_limit=30):
        self.accesstoken =accesstoken
        self.sessionid =sessionid
        self.ignoreaccounts =ignore_accounts.split()
        self.fromday =fromday
        self.today =today
        self.useragent ='Mozilla/5.0 (X11; Windows x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
        self.requests_limit =requests_limit
        self.enrolls_limit =enrolls_limit
        self.isthour =5
        self.istminute =30

    def request_resource(self, url, method='get', headers={}, cookies={}, data={}, json={}, allow_redirectects=True, proxies={}, verify=False):
        while True:
            try:
                if method.lower()=='get': return requests.get(url, headers=headers, cookies=cookies, data=data, json=json, allow_redirects=allow_redirectects, proxies=proxies, verify=verify)
                elif method.lower()=='post': return requests.post(url, headers=headers, cookies=cookies, data=data, json=json, allow_redirects=allow_redirectects, proxies=proxies, verify=verify)
            except (requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.SSLError): continue

    def get_courseid(self, data):
        datas =data.split('https://img-c.udemycdn.com/course/')
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

    def get_coupon_status(self, course_id, coupon):
        json_data =self.request_resource(
            f'https://www.udemy.com/api-2.0/course-landing-components/{course_id}/me/?components=purchase,redeem_coupon,discount_expiration&discountCode={coupon}',
            headers={'User-Agent': self.useragent}
        )
        json_data =json_data.json()
        if not json_data.get('redeem_coupon'):return
        status =json_data['redeem_coupon']['discount_attempts'][0]['status']
        if status=='applied':return {
            'uses_remaining':json_data['purchase']['data']['pricing_result']['campaign']['uses_remaining'],
            'real_price':json_data['purchase']['data']['pricing_result']['list_price']['amount'],
            'end_time':[json_data['discount_expiration']['data']['discount_deadline_text'] if json_data.get('discount_expiration') else ''][0]
        }


    def collect_offer(self, offer, coupon_datas, wrong_datas, thread):
        result_page =self.request_resource(f'https://www.real.discount{offer[0]}').text
        coupon_links =BeautifulSoup(result_page, 'html.parser').findAll('a')
        for coupon_link in coupon_links:
            if 'https://www.udemy.com/course/' in coupon_link.get('href', ''):
                coupon_datas.append([offer[1], coupon_link['href'].split('murl=')[-1]])
                break
        else: wrong_datas.append(offer[1])
        thread[0] -=1

    def check_offer(self, coupon_data, avail_offers, wast_offers, final_offers, thread):
        course_title =coupon_data[0]
        course_name =coupon_data[1].split('/')[-2]
        coupon_code =coupon_data[1].split('=')[-1]
        course_id, result_json =None, None
        while True:
            try:
                if not course_id: course_id =self.get_courseid(self.request_resource(coupon_data[1]).text)
                if not result_json: result_json =self.get_coupon_status(course_id, coupon_code)
                if course_id: break
            except Exception: pass
        coupon_data =[]
        if result_json and result_json.get('uses_remaining'):
            while True:
                result_page =self.request_resource(f'https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/', headers={'User-Agent': self.useragent}, cookies={'access_token': self.accesstoken})
                if result_page.status_code<500: break
            if result_page.status_code==403 and not result_page.text.lower()=='resource not found':
                assign_avail =True
                for accesstoken in self.ignoreaccounts:
                    while True:
                        result_page =self.request_resource(f'https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/', headers={'User-Agent': self.useragent}, cookies={'access_token': accesstoken})
                        if result_page.status_code<500: break                      
                    if result_page.status_code!=403: assign_avail =False
                if assign_avail:
                    update ='Available'
                    final_offers.append({
                            "discountInfo":{"code":coupon_code},
                            "price":{"amount":0,"currency":"INR"},
                            "buyable":{"id":course_id,"type":"course"}
                    })
                    for data in [course_name, course_id, coupon_code, update, int(result_json.get('real_price')), result_json.get('end_time'), result_json['uses_remaining']]: coupon_data.append(data)
                    avail_offers.append(coupon_data)
                else:
                    update ='Enrolled'
                    for data in [course_name, course_id, coupon_code, update, int(result_json.get('real_price', 0)), result_json.get('end_time'), result_json.get('uses_remaining')]: coupon_data.append(data)
                    wast_offers.append(coupon_data)    
            else:
                update ='Enrolled'
                for data in [course_name, course_id, coupon_code, update, int(result_json.get('real_price', 0)), result_json.get('end_time'), result_json.get('uses_remaining')]: coupon_data.append(data)
                wast_offers.append(coupon_data)
        else:
            update ='Expired'
            for data in [course_name, course_id, coupon_code, update, int(result_json.get('real_price', 0) if result_json else 0), '', 0]: coupon_data.append(data)
            wast_offers.append(coupon_data)
        thread[0] -=1
        try: print(course_title+f' [{update}]')
        except: pass
        coupon_data.append(course_title)

    def enroll_course(self, db, db_notify, courses):
        try:
            common_data ={
                "checkout_environment":"Marketplace",
                "checkout_event":"Submit",
                "shopping_info":{"items":courses,"is_cart":False},
                "payment_info":{"method_id":"0","payment_vendor":"Free","payment_method":"free-method"}
            }
            cookies={'access_token': self.accesstoken, 'dj_session_id': self.sessionid}
            if os.environ.get('CF_CLEARANCE'): cookies['cf_clearance'] =os.environ['CF_CLEARANCE']
            result_page =self.request_resource('https://www.udemy.com/payment/checkout-submit/', data=json.dumps(common_data), headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Content-Type': 'application/json'}, cookies=cookies, method='POST')
            result_json =result_page.json()
            if result_json.get('status')=='succeeded':update ='Succeeded'
            else:
                update ='Failed'
                if 'You do not have permission to perform this action' in result_json.get('detail', ''):
                    self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Error-Critical", "Enroll Failed, Session id or Access Token is Expired")
                    raise Exception('Enroll Fail, Session id or Access Token is Expired...\n')
            if not result_json.get('status')=='succeeded': self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Error-UnKnown", "UnKnown Error")
        except json.JSONDecodeError:
            if result_page.status_code==504:update ='Succeeded'
            else:print(result_page.text);update ='Error'
        return update
    

    def realdiscount(self, db, db_table, db_notify):
        
        if not coupon_datas:
            self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Info-High", "No Free Courses Available")
            print('> Free Course Offers Not Found..\n')
            return 1
        
        avail_offers, wast_offers, old_offers, final_offers =[], [], [], []
        print('\n\n> Checking Offers For Enrolling...\n')
        thread =[0]
        for coupon_data in range(len(coupon_datas)):
            if coupon_datas[coupon_data][1] in old_coupons:
                try:print(coupon_datas[coupon_data][0]+f' [Old Coupon]'); 
                except: pass
                old_offers.append(coupon_datas[coupon_data][1])
            else:
                Thread(target=self.check_offer, args=[coupon_datas[coupon_data], avail_offers, wast_offers, final_offers, thread]).start()
                thread[0] +=1
            while (thread[0]>=self.requests_limit and coupon_data<len(coupon_datas)-1)  or coupon_data==len(coupon_datas)-1:
                sleep(0.5)
                print(f"\t{len(avail_offers)+len(wast_offers)+len(old_offers)}/{len(coupon_datas)}", end='\r')
                if len(avail_offers)+len(wast_offers)+len(old_offers)==len(coupon_datas): break

        if not avail_offers:
            print('\n\n> Courses Not Valid For Enrolling..\n')
            if wast_offers:
                if self.make_cache(db, db_table, wast_offers):
                    self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Info-Low", "Success, Enrolled and Expired Datas Updated, But No Free Courses Available")
                    print('> Success, Enrolled and Expired Datas Updated...\n')
                else:
                    self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Error-High", "Failed, Enrolled and Expired datas Update to Database")
                    raise Exception('Fail, Enrolled and Expired Datas Update...\n')
            else:
                self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Info-Normal", "No Datas Available for Update to Database")
                print('> No Datas For Update...\n')
            return 1

        print('\n\n> Valid Courses..\n')
        for id, data in enumerate(avail_offers, start =1):
            try: print(f'{id}. {data[-1]}')
            except: pass
        print('\n> Enrolling Courses..\n')
        bundle_size =self.enrolls_limit
        total_bundle =len(final_offers)//bundle_size
        remaining =len(final_offers)%bundle_size
        total_status =[]
        for bundle in range(1, total_bundle+1): total_status.append(self.enroll_course(db, db_notify, final_offers[bundle_size*bundle-bundle_size:bundle_size*bundle]))
        else:
            if total_bundle and remaining:total_status.append(self.enroll_course(db, db_notify, final_offers[bundle_size*total_bundle:]))
            elif not total_bundle and remaining:total_status.append(self.enroll_course(db, db_notify, final_offers))
        print(f"> Total Courses: {len(final_offers)}, Status: {total_status}\n")
        for status in total_status:
            if status != 'Succeeded':
                if self.make_cache(db, db_table, wast_offers):
                    self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Info-High", "Success, Enrolled and Expired datas Update to Database, The Program Refetching the Courses for Try To Again Enroll")
                    print('> Success, Enrolled and Expired Datas Updated...\n')
                else:
                    self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Error-High", "Failed, Enrolled and Expired datas Update to Database, The Program Refetching the Courses for Try To Again Enroll")
                    raise Exception('Fail, Enrolled and Expired Datas Update...\n')
                return 0
        else:
            if self.make_cache(db, db_table, wast_offers+avail_offers):
                self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Info-Normal", f"Success, datas Updated to Database, {len(final_offers)} Courses Enrolled")
                print('> Success, Datas Updated...\n')
            else:
                self.send_Notify(db, db_notify, "Free-Courses-Udemy", "Error-High", "Failed, All datas Update to Database")
                raise Exception('Fail, Datas Update...\n')
        return 1

def main():
    infinity_db =Infinitydatabase(os.environ['DB_ADMIN_URL'])
    # infinity_db =Infinitydatabase(os.environ['DB_ADMIN_URL'])
    # rdiscount =Realdiscount(os.environ['ACCESS_TOKEN'], os.environ['SESSION_ID'], os.environ['IGNORE_ACCESSTOKEN'],
    rdiscount =Realdiscount(os.environ['ACCESS_TOKEN'], os.environ['SESSION_ID'], os.environ['IGNORE_ACCESSTOKEN'],
        int(os.environ['FROM_DAY']), int(os.environ['TO_DAY']), int(os.environ['REQUESTS_LIMIT']), int(os.environ['ENROLLS_LIMIT']))
    while True:
        if rdiscount.realdiscount(infinity_db, os.environ['DB_TABLE_NAME'], os.environ['DB_TABLE_NOTIFY']): break

if __name__ == '__main__':
    main()