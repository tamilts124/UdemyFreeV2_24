import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

driver =None

def launch_udemy_login(email: str, password: str)->[bool, list]:
    '''Return data will be cookies with login status like [status, cookies].
       If the status is False, the login is required otp
    '''
    global driver
    driver = uc.Chrome()
    driver.get(r'https://www.udemy.com/join/passwordless-auth/?locale=en_US&next=https%3A%2F%2Fwww.udemy.com%2F&response_type=html')
    sleep(5)

    email_field =driver.find_element(By.NAME, 'email')
    email_field.send_keys(email)
    sleep(1)

    password_field =driver.find_element(By.NAME, 'password')

    if password_fied:
        password_field.send_keys(password)
        sleep(1)
        login_button =driver.find_element(By.CLASS_NAME, 'helpers--auth-submit-button--W3Tqk')
        login_button.click()
        sleep(10)
        cookies =driver.get_cookies()
        sleep(1)
        driver.close()
        return [True, cookies]

    else:
        form =driver.find_element(By.CSS_SELECTOR, 'form[data-purpose=code-generation-form]')
        submit_button =form.find_element(By.CSS_SELECTOR, 'button')
        submit_button.click()
        sleep(20)
        return [False, []]

def submit_otp(otp:int)->list:
    otp_field =driver.find_element(By.CSS_SELECTOR, 'input[placeholder="6-digit code"]')
    otp_field.send_keys(otp)
    sleep(1)

    div_element =driver.find_element(By.CLASS_NAME, 'auth-form-row--small--Byo8R')
    login_button =div_element.find_element(By.TAG_NAME, 'button')
    login_button.click()
    sleep(10)

    cookies =driver.get_cookies()

    # print(cookies)
    sleep(1)
    driver.close()
    return cookies


