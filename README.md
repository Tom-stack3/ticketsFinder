# Tickets Finder
*ticketsFinder* is a Python script that looks for available tickets for Mount Hermon
and sends an alert in Real-Time to all the emails interested.\
It looks for available tickets in all the dates available for sale.

## How it works:
Upon execution, the script asks for how many minutes the program should be running.
Then the program asks for the email addresses to send alerts to.
After giving the needed parameters, the script starts searching for tickets.

Every 30 seconds, using selenium, it gets the HTML of the tickets page.
Then it checks all the dates available for sale to see if there are dates with available tickets.
The script saves the free dates in a list and then send email alerts to all the emails.
If an email was sent (if available tickets were found), the script waits 10 minutes before checking again for tickets.

## Setup before run:

### Installations:
**Libraries used**:  
1. selenium - ```pip install selenium```
2. Beautiful Soup - ```pip install beautifulsoup4```

 **Selenium setup:**
The script works with selenium Firefox, so inorder to run the script,
Firefox needs the be installed.
#### Linux:
In order to work with the selenium firefox-geckodriver, it needs to be installed:
```shell
sudo apt-get install firefox-geckodriver
```
#### Windows:
* To work with selenium.webdriver, [geckodriver](https://github.com/mozilla/geckodriver/releases/tag/v0.29.0) needs to be installed.\
After installing and extracting the geckodriver.exe, put it in one of System PATHs.
To find your System PATHs:

  *from: https://www.mathworks.com/matlabcentral/answers/94933-how-do-i-edit-my-system-path-in-windows*

  In Windows, environment variables can be accessed from “Advanced system settings” on the left side of the “System” control panel.
  How you access and edit the environment variables depends on the version of Windows you are using.\
  **Windows 10 (Also Windows 8.1):**
    1. Right-click on the Start Button
    2. Select “System” from the context menu.
    3. Click “Advanced system settings”
    4. Go to the “Advanced” tab
    5. Click “Environment Variables…”
    6. Click variable called “Path” and click “Edit…”
    
  Now choose one of the PATHs shown, (the python one is prefered) and just copy geckodriver.exe there.
  
 ### Code setup:
   The program sends alerts to the emails specified in the begining of the run.\
   Change the following lines in the `config.yaml` file: (lines 2-3)
   ```yaml
   # ===== Email settings =====
   email_address: example@mail.com
   email_password: password_example
   ```
   So before running the script, you need to fill in a working email address and a password for the email address you want the program to send the alerts from.
 
 ## Running the script:
 After the setup, just run the python script.\
 Enter the time in minutes you want the scriot to keep checking for tickets.\
 Then enter the email addresses you want to be alerted seperated by a comma.\
 like this:\
 ``` mail.1@mail.com, example@example.com, cr7@real.madrid```
 
 That's it!
 Have fun skiing in the Hermon :)

## Run example:

![run example](https://raw.githubusercontent.com/Tom-stack3/ticketsFinder/main/img/run_example.png)  
