import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

tickets_url = 'https://hermon.pres.global/vouchers'


# we get the html of the page using selenium.
# we use selenium inorder to load the page after the javascript had already ran and the calendar shows up.
# then we use BeautifulSoup to work easily with the html loaded.
def get_soup_page(url):
    opts = Options()
    opts.headless = True
    assert opts.headless  # Operating in headless mode
    browser = Firefox(options=opts)
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.close()
    return soup


def find_available():
    today = datetime.date.today()
    soup = get_soup_page(tickets_url)
    dates_available = []
    for day_index in range(0, 5 * 7):
        date = today + datetime.timedelta(days=day_index)
        # format: 2021-02-06
        date_in_format = date.strftime("%Y-%m-%d")
        search_result = soup.find("div", {"data-date": date_in_format})
        # if the day doesn't exist - means we got to the end of the calendar.
        if search_result is None:
            break
        if 'אזל' in str(search_result):
            continue
            # print(date_in_format, ':(')
        elif 'יש' in str(search_result):
            print(date_in_format, 'HERE!!')
            dates_available.append(date_in_format)
        else:
            print(date_in_format, 'failed')
    return dates_available


# we generate the content of the email.
# we send a list of the dates available, the link to buy the tickets,
# and the current time and date
def email_content(dates_available):
    today = datetime.datetime.now()
    text = 'Available dates:\n'
    for date in dates_available:
        text += date + '\n'
    text += '\nlink to buy: ' + tickets_url
    text += '\n\ntime checked: ' + today.strftime("%X %d/%m/%Y")
    return text


# send the email with the available tickets to the recipients
def send_mail(recipients, dates_available):
    body = email_content(dates_available)
    msg = MIMEMultipart()

    # change this to an email you want the alerts of the bot to be sent from
    email_address = 'example@gmail.com'
    # change this to the password for the email you chose
    email_pass = 'password_example'

    msg['Subject'] = 'Found available tickets to Hermon!'
    msg['From'] = email_address
    msg['Bcc'] = ', '.join(recipients)

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address, email_pass)
    server.send_message(msg)
    server.quit()


def main():
    # here we get the params to run with.
    minutes_to_run = input("Time to keep checking (in minutes):")
    while not minutes_to_run.isnumeric() or int(minutes_to_run) > 34 * 60:
        minutes_to_run = input("Time to keep checking (in minutes):")
    email_addresses = input("Email addresses to send alerts to (separated by commas):\n")
    recipients = [email.strip() for email in email_addresses.split(',')]

    # the time to wait before searching for tickets again after finding.
    # in seconds
    wait_time_after_finding = 600

    # the time to wait after searching for tickets (and didn't find) before searching again.
    # in seconds
    wait_time_after_search = 30

    print("\n--- started search ---\n")
    start_time = time.time()
    end_time = start_time + 60 * int(minutes_to_run)
    while time.time() < end_time:
        dates_available = find_available()
        # if list not empty, means we found some tickets
        if dates_available:
            print('dates_available', dates_available)
            send_mail(recipients, dates_available)
            # if there is no time left, we can save the wait
            if time.time() + wait_time_after_finding > end_time:
                break
            time.sleep(wait_time_after_finding)
        else:
            # if there is no time left, we can save the wait
            if time.time() + wait_time_after_search > end_time:
                break
            time.sleep(wait_time_after_search)
    print("\n--- search ended ---\n")
    print("run ended after:", (time.time() - start_time) / 60, "minutes")


if __name__ == '__main__':
    main()
