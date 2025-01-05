# Udemy Auto Enroll Bot

This repository contains a GitHub Action workflow that allows you to automatically enroll in Udemy courses using coupons scraped from various websites. The bot efficiently handles the login process and course enrollment with the help of Google Mail and app passwords. It stores and manages session cookies securely to minimize repeated logins.

## Features

- **Automated Udemy Course Enrollment:** Enroll in Udemy courses automatically using a GitHub Action cron job.
- **Session Cookie Management:** Utilizes Udemy session cookies stored securely in the GitHub Action cache, encrypted using AES.
  - Cookies are reused until they expire. Upon expiry, the bot logs in again to refresh cookies.
- **Dual Login Methods:**
  - Email + Google App Password for passwordless OTP-based login.
  - Email + Udemy Password for direct login when required.
- **Scraping Coupons:** Retrieves course coupons from the following sources:
  - [Real.discount](https://www.real.discount)
  - [CouponScorpion](https://www.couponscorpion.com)
  - [CourseVania](https://www.coursevania.com)
  - [CourseJoiner](https://www.coursejoiner.com)
  - [DiscUdemy](https://www.discudemy.com)
  - [Infognu](https://www.infognu.com)
  - [UdemyFreebies](https://www.udemyfreebies.com)
  - [YoFreeSamples](https://www.yofreesamples.com)

## Setup Instructions

1. **Fork and Clone Repository:**
   - Fork this repository to your GitHub account and clone it locally.

2. **Set Up GitHub Secrets:**
   Add the following secrets to your repository:
   
   - **`SECURE_KEY`**: Encryption key for storing session cookies securely in the GitHub Action cache.
   - **`EMAIL`**: Your Udemy account email address.
   - **`PASSWORD`**: Your Udemy account password.
   - **`GMAIL_APP_PASSWORD`**: Google app password for the email account used to log in to Udemy.
   - **`MYACCESSTOKENS`**: Comma-separated Udemy tokens from your other accounts to avoid enrolling in the same course multiple times.
   - **Optional:**
     - **`ACCESS_TOKEN`**: Use your Udemy access token for login instead of providing email and password.
     - **`SESSION_ID`**: Use your Udemy session ID for login.

3. **Customize Cron Schedule:**
   - The workflow is triggered using a cron schedule. You can adjust the schedule in the GitHub Actions workflow file (`.github/workflows/enroll.yml`).

4. **Run the Workflow:**
   - Once set up, the GitHub Action will automatically scrape course coupons and enroll you in available courses as per the schedule.

## How It Works

1. **Login Process:**
   - The bot attempts to log in using email and Google app password for OTP-based authentication.
   - If OTP-based login fails, it falls back to direct login using email and Udemy password.

2. **Cookie Management:**
   - After logging in, the session cookies are encrypted using the AES algorithm with the `SECURE_KEY` and stored in the GitHub Action cache.
   - This reduces the need for repeated logins, improving efficiency.

3. **Course Enrollment:**
   - Scrapes course coupons from supported websites.
   - Uses the scraped coupons to enroll in free Udemy courses automatically.

4. **Token Avoidance:**
   - To prevent enrolling the same course across multiple accounts, the bot checks tokens stored in `MYACCESSTOKENS`.

## Environment Variables

| Secret Name         | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `SECURE_KEY`        | AES encryption key for securing session cookies.                          |
| `EMAIL`             | Your Udemy account email address.                                         |
| `PASSWORD`          | Your Udemy account password.                                              |
| `GMAIL_APP_PASSWORD`| Google app password for OTP-based login.                                  |
| `MYACCESSTOKENS`    | Comma-separated tokens to prevent duplicate course enrollment.            |
| `ACCESS_TOKEN`      | (Optional) Udemy access token for session-based login.                    |
| `SESSION_ID`        | (Optional) Udemy session ID for session-based login.                      |

## Notes

- This bot uses a combination of scraping and automation. Ensure you comply with Udemy's terms of service and the terms of the coupon-providing websites.
- It is recommended to rotate your encryption key periodically for enhanced security.

## Contributing

Feel free to submit issues or contribute to this project by opening a pull request. Suggestions and improvements are always welcome!

## License

This project is licensed under the [MIT License](LICENSE).

