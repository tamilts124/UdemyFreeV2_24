import imaplib
import email
from email.header import decode_header, make_header
from email.utils import parseaddr
import datetime

class EmailReader:
    def __init__(self, username, app_password, imap_server="imap.gmail.com"):
        """
        Initialize the EmailReader with credentials and IMAP server details.
        """
        self.username = username
        self.app_password = app_password
        self.imap_server = imap_server
        self.connection = None

    def connect(self):
        """
        Connect to the IMAP server and log in with provided credentials.
        """
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server)
            self.connection.login(self.username, self.app_password)
            print("Connected successfully!")
        except Exception as e:
            print(f"Error during connection: {e}")

    def list_mailboxes(self):
        """
        List all available mailboxes (folders) in the email account.
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return

        try:
            status, folders = self.connection.list()
            if status == "OK":
                print("Available Mailboxes:")
                for folder in folders:
                    print(folder.decode())
            else:
                print("Failed to retrieve mailboxes.")
        except Exception as e:
            print(f"Error listing mailboxes: {e}")

    def fetch_emails(self, mailbox="inbox", limit=10):
        """
        Fetch emails from the specified mailbox (default is "inbox").
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return []
        
        try:
            self.connection.select(mailbox)
            status, messages = self.connection.search(None, "ALL")
            email_ids = messages[0].split()
            
            # Limit the number of emails to fetch
            email_ids = email_ids[-limit:]
            
            emails = []
            for msg_id in email_ids:
                res, msg = self.connection.fetch(msg_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        email_data = self.parse_email(msg)
                        emails.append(email_data)
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def parse_email(self, msg):
        """
        Parse the raw email message and return its components.
        """
        try:
            # Decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                try:
                    subject = subject.decode(encoding if encoding else "utf-8")
                except (UnicodeDecodeError, TypeError):
                    subject = subject.decode("latin-1")  # Fallback to latin-1 if UTF-8 fails
            else:
                subject = str(subject)  # Ensure subject is a string, in case it's already decoded

            # Extract sender information
            sender = msg.get("From")
            sender = str(sender)  # Ensure sender is a string, even if it's a Header object

            # Extract the email body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode()
                        except (UnicodeDecodeError, TypeError):
                            body = part.get_payload(decode=True).decode("latin-1")  # Fallback to latin-1 if UTF-8 fails
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode()
                except (UnicodeDecodeError, TypeError):
                    body = msg.get_payload(decode=True).decode("latin-1")  # Fallback to latin-1 if UTF-8 fails

            return {"subject": subject, "sender": sender, "body": body}
        except Exception as e:
            print(f"Error parsing email: {e}")
            return {"subject": None, "sender": None, "body": None}

    def filter_emails_by_subject(self, keyword, mailbox="inbox", limit=10):
        """
        Filter emails containing a specific keyword in the subject.
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return []

        try:
            self.connection.select(mailbox)
            status, messages = self.connection.search(None, "ALL")
            email_ids = messages[0].split()
            
            filtered_emails = []
            for msg_id in email_ids:
                res, msg = self.connection.fetch(msg_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        if keyword.lower() in subject.lower():
                            email_data = self.parse_email(msg)
                            filtered_emails.append(email_data)

                # Check if limit is reached
                if len(filtered_emails) >= limit:
                    break

            return filtered_emails
        except Exception as e:
            print(f"Error filtering emails by subject: {e}")
            return []

    def filter_emails_by_date(self, date, mailbox="inbox", limit=10):
        """
        Filter emails from a specific date (YYYY-MM-DD).
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return []

        try:
            self.connection.select(mailbox)
            # Convert date to IMAP format
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%b-%Y")
            status, messages = self.connection.search(None, f'ON {formatted_date}')
            email_ids = messages[0].split()

            filtered_emails = []
            for msg_id in email_ids:
                res, msg = self.connection.fetch(msg_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        email_data = self.parse_email(msg)
                        filtered_emails.append(email_data)

                # Check if limit is reached
                if len(filtered_emails) >= limit:
                    break

            return filtered_emails
        except Exception as e:
            print(f"Error filtering emails by date: {e}")
            return []


    def filter_emails_by_sender(self, sender_email, mailbox="inbox", limit=10):
        """
        Filter emails from a specific sender.
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return []

        try:
            self.connection.select(mailbox)
            status, messages = self.connection.search(None, "ALL")
            email_ids = messages[0].split()

            # Limit the number of emails to fetch
            email_ids = email_ids[-limit:]

            filtered_emails = []
            for msg_id in email_ids:
                res, msg = self.connection.fetch(msg_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])

                        # Extract and decode the raw 'From' field
                        sender = msg.get("From")
                        decoded_sender = self.decode_header(sender)

                        # Parse the 'From' field using parseaddr to handle complex formats
                        _, email_address = parseaddr(decoded_sender)

                        # Compare the email address part only
                        if sender_email.lower() in email_address.lower():
                            email_data = self.parse_email(msg)
                            filtered_emails.append(email_data)

                return filtered_emails
        except Exception as e:
            print(f"Error filtering emails by sender: {e}")
            return []

    def decode_header(self, header):
        """
        Decodes the email header that might have special characters or encodings.
        """
        try:
            # Decode the header using make_header
            decoded_header = str(make_header(decode_header(header)))
            return decoded_header
        except Exception as e:
            return header  # Return the raw header if decoding fails

    def filter_emails_combined(self, subject=None, sender_email=None, date=None, mailbox="inbox", limit=10):
        """
        Apply multiple filters: subject, sender, and date.
        """
        if not self.connection:
            print("Not connected. Please connect first.")
            return []

        try:
            self.connection.select(mailbox)
            
            # Format the date to the IMAP required format (DD-Mon-YYYY)
            if date:
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d-%b-%Y")
                search_query = f'ON {formatted_date}'
            else:
                search_query = "ALL"

            status, messages = self.connection.search(None, search_query)
            email_ids = messages[0].split()
            
            filtered_emails = []
            for msg_id in email_ids:
                res, msg = self.connection.fetch(msg_id, "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        email_data = self.parse_email(msg)
                        
                        # Check if email matches all specified filters
                        if subject and email_data["subject"] and subject.lower() not in email_data["subject"].lower():
                            continue
                        if sender_email and email_data["sender"] and sender_email.lower() not in email_data["sender"].lower():
                            continue
                        
                        filtered_emails.append(email_data)

                # Break if limit reached
                if len(filtered_emails) >= limit:
                    break

            return filtered_emails

        except Exception as e:
            print(f"Error applying combined filters: {e}")
            return []

    def is_email_on_date(self, msg, date):
        """
        Check if the email was sent on the specific date.
        """
        try:
            date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d-%b-%Y")
            email_date = msg["Date"]
            email_date_parsed = email.utils.parsedate_tz(email_date)
            email_date_obj = datetime.datetime.fromtimestamp(email.utils.mktime_tz(email_date_parsed))

            # Compare the dates
            return email_date_obj.strftime("%d-%b-%Y") == formatted_date
        except Exception as e:
            print(f"Error checking email date: {e}")
            return False

    def close_connection(self):
        """
        Close the IMAP connection.
        """
        if self.connection:
            self.connection.close()
            self.connection.logout()
            print("Connection closed.")

# Example Usage
if __name__ == "__main__":
    # Replace with your credentials
    username = "mail"
    app_password = "password"

    email_reader = EmailReader(username, app_password)
    email_reader.connect()

    # Example of fetching and filtering emails
    emails = email_reader.fetch_emails(limit=5)
    for email_data in emails:
        print(f"Subject: {email_data['subject']}")
        print(f"Sender: {email_data['sender']}")
        print(f"Body: {email_data['body']}\n")

    email_reader.close_connection()


    #emails = email_reader.fetch_emails('[Gmail]/Spam', limit=5)  # Fetch the latest 5 emails

    # for idx, email_data in enumerate(emails, 1):
    #     print(f"Email {idx}")
    #     print(f"Subject: {email_data['subject']}")
    #     print(f"Sender: {email_data['sender']}")
    #     print(f"Body: {email_data['body']}\n")

    #email_reader.close_connection()

# if __name__ == "__main__":
    # # Replace these with your credentials
    # username = "your_email@gmail.com"
    # app_password = "your_app_password"

    # email_reader = EmailReader(username, app_password)
    # email_reader.connect()

    # # Filter emails by subject
    # subject_keyword = "Meeting"
    # filtered_by_subject = email_reader.filter_emails_by_subject(subject_keyword)
    # print(f"Emails with '{subject_keyword}' in the subject:")
    # for email in filtered_by_subject:
    #     print(email)

    # # Filter emails by sender
    # sender_email = "example@domain.com"
    # filtered_by_sender = email_reader.filter_emails_by_sender(sender_email)
    # print(f"Emails from '{sender_email}':")
    # for email in filtered_by_sender:
    #     print(email)

    # # Filter emails by date
    # specific_date = "2024-12-01"
    # filtered_by_date = email_reader.filter_emails_by_date(specific_date)
    # print(f"Emails from '{specific_date}':")
    # for email in filtered_by_date:
    #     print(email)

    # email_reader.close_connection()

