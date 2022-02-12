#!/usr/bin/env python3

import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
import getopt
import sys

config = {}
opts = Options()


def log(*args):
    """
    Log a message.
    """
    print('[+]', *args)


verboseprint = log


def get_soup_of_page(url: str) -> BeautifulSoup:
    """
    Get the html of the page using Selenium, load the html into a BeatifulSoup object and return it.
    """
    browser = Firefox(options=opts)
    verboseprint(f"Getting html of {url}")
    browser.get(url)
    # wait for the calendar to appear
    # solution from: http://allselenium.info/wait-for-elements-python-selenium-webdriver/
    wait = WebDriverWait(browser, 10)
    wait.until(ec.visibility_of_element_located(
        (By.XPATH, "//div[@class='v-calendar-weekly__day-label']")))

    verboseprint("Parsing html using BeautifulSoup..")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.close()
    return soup


def find_available_tickets() -> list:
    """
    Find and return a list of available dates.
    """
    today = datetime.date.today()
    soup = get_soup_of_page(config["tickets_url"])
    dates_available = []
    for day_index in range(1, 5 * 7):
        date = today + datetime.timedelta(days=day_index)
        # format: 2021-02-06
        date_in_format = date.strftime("%Y-%m-%d")
        search_result = soup.find("div", {"data-date": date_in_format})
        # if the day doesn't exist - means we got to the end of the calendar.
        if search_result is None:
            break
        # if there are no tickets for sale for that day
        if config["closed_keyword"] in str(search_result):
            continue
        elif config["success_keyword"] in str(search_result):
            log(f"{date_in_format} has tickets for sale!")
            dates_available.append(date_in_format)
        else:
            log(f"Failed to get information on {date_in_format}!")
    return dates_available


def generate_email_body(dates_available) -> str:
    """
    Generate the email body.
    """
    today = datetime.datetime.now()
    text = 'Available dates:\n'
    for date in dates_available:
        text += date + '\n'
    text += f"""\

Buy tickets here: {config["tickets_url"]}

Checked at: {today.strftime("%X %d/%m/%Y")}
    """
    return text


def send_email(recipients, dates_available) -> None:
    """
    Send an email with the available tickets to the specified recipients.
    """
    # generate the email body
    body = generate_email_body(dates_available)

    msg = MIMEMultipart()

    msg['Subject'] = 'Found available tickets to Hermon!'
    msg['From'] = config["email_address"]
    msg['Bcc'] = ', '.join(recipients)

    # add the body to the body of the email
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(config["email_address"], config["email_password"])
    server.send_message(msg)
    server.quit()


def usage():
    """
    Print the usage information.
    """
    print(f"""Usage: {sys.argv[0]} [OPTION]...

\t-t <minutes to run>, --time=<minutes to run>\tspecify duration of the script execution (in minutes)
\t-r <list of recipients>, --recipients=<list of recipients>\tspecify the list of emails wish to receive alerts about available tickets
\t-d, --debug\tload configuration settings from debug-config.yaml instead
\t-v, --verbose\texplain what is being done
\t-h, --help\tdisplay this help list and exit
""")


def parse_args():
    """
    Parse the arguments from the command line.
    """
    args_list = sys.argv[1:]
    global config
    global opts
    global verboseprint

    # short options
    short_options = "ht:r:vd"
    # long options
    long_options = ["help", "time=", "recipients=", "verbose", "debug"]

    config_path = "config.yaml"
    specified_config = {}
    # parse the arguments
    try:
        arguments, values = getopt.getopt(
            args_list, short_options, long_options)
        # checking each argument
        for current_arg, current_val in arguments:
            if current_arg in ("-h", "--help"):
                # print the usage information and exit
                usage()
                sys.exit(0)

            elif current_arg in ("-t", "--time"):
                # if the value received is not numeric or a negative number
                if not current_val.isnumeric() or int(current_val) < 0:
                    raise Exception(
                        "Time to run should be numeric and positive")
                specified_config["time_to_run"] = current_val

            elif current_arg in ("-r", "--recipients"):
                specified_config["recipients"] = current_val

            # if the verbose flag is specified
            elif current_arg in ("-v", "--verbose"):
                specified_config["verbose"] = True

            # if the debug option is specified
            elif current_arg in ("-d", "--debug"):
                config_path = "debug-config.yaml"

    except Exception as err:
        # output error, and return with an error code
        print(f"Error parsing the arguments! {err}\n")
        usage()
        sys.exit(2)

    # load the right configuration file
    with open(config_path, 'r') as input_file:
        config = yaml.load(input_file, yaml.FullLoader)

    # update the configuration with the specified options
    for arg, val in specified_config.items():
        config[arg] = val

    # if not in verbose mode
    if not config["verbose"]:
        verboseprint = lambda *args: None

    # if operating in headless mode
    if config["headless"]:
        opts.headless = True
        verboseprint("Operating in headless mode..")


def main() -> None:
    parse_args()
    minutes_to_run = config["time_to_run"]
    email_addresses = config["recipients"].strip(",")
    verboseprint(f"Running for {minutes_to_run} minutes")
    verboseprint(
        f"Sending emails to the following recipients: {email_addresses}")
    recipients = [email.strip() for email in email_addresses.split(',')]

    # time to wait before searching again after finding tickets (in seconds)
    wait_after_find = config["wait_after_find"]

    # time to wait before searching again after not finding tickets (in seconds)
    wait_after_search = config["wait_after_search"]

    log("Started search")
    start_time = time.time()
    end_time = start_time + 60 * int(minutes_to_run)
    while time.time() < end_time:
        # print an empty line
        print()
        # get a list of available dates
        dates_available = find_available_tickets()
        # if list not empty, means we found some tickets
        if dates_available:
            # inform the recipients
            verboseprint("Sending an email about the available tickets")
            send_email(recipients, dates_available)

            # if there is no time left, there is no need to wait
            if time.time() + wait_after_find > end_time:
                break
            verboseprint(f"Sleeping for {wait_after_find} seconds..")
            time.sleep(wait_after_find)
        else:
            # if there is no time left, there is no need to wait
            if time.time() + wait_after_search > end_time:
                break
            verboseprint(f"Sleeping for {wait_after_search} seconds..")
            time.sleep(wait_after_search)
    log("Search ended after:", (time.time() - start_time) / 60, "minutes")


if __name__ == '__main__':
    main()
