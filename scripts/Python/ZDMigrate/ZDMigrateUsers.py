from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import requests
import time


# Some persistent browser stuff
# ------------------------------------------------------------------------
driver = None


def get_or_create_browser():

    global driver
    driver = driver or webdriver.Firefox()
    driver.get('javascript:localStorage.clear();')
    driver.delete_all_cookies()
    return driver

get_or_create_browser()


# Some element wait stuff
# ------------------------------------------------------------------------
global wait
wait = WebDriverWait(driver, 10)


# User is created with standard JIRA permissions using the User API
# ------------------------------------------------------------------------
def create_user(username):

    user_create_url = 'https://janrain.atlassian.net/rest/api/2/user'
    user_create_payload = dict(
            name="placeholder"
            , emailAddress="placeholder"
            , displayName="placeholder"
    )
    user_create_payload["name"] = username
    user_create_payload['emailAddress'] = username+'@janrain.com'
    user_create_payload['displayName'] = username
    user_create_payload = json.dumps(user_create_payload)
    user_create_headers = {'Content-type': 'application/json'}
    post_request = requests.post(
            user_create_url
            , data=user_create_payload
            , headers=user_create_headers
            , auth=('username_here', 'password_here')
    )
    post_data = post_request
    print post_data.text

create_user('someMigrate')


# Login with the JIRA admin user who will perform actions on the ZD users
# ------------------------------------------------------------------------
def login(username, password):

    # Login Page
    login_url = 'https://janrain.atlassian.net/login'
    driver.get(login_url)

    # Login Page Elements
    user_elem = driver.find_element_by_name("username")
    pass_elem = driver.find_element_by_name("password")
    login_elem = driver.find_element_by_id("login")

    # Login Page Actions
    user_elem.send_keys(username)
    pass_elem.send_keys(password)
    login_elem.send_keys(Keys.RETURN)
    time.sleep(3)
login('username_here', 'password_here')


# User access rights are updated through the UI using Selenium
# ------------------------------------------------------------------------
def update_access(username):

    # users/view
    user_access_url = 'https://janrain.atlassian.net/admin/users/view?username=%s' % username
    driver.get(user_access_url)

    # Am I on the right page?
    user_title_elem = wait.until(EC.presence_of_element_located((By.ID, "user-name-title")))
    assert "someMigrate" == user_title_elem.text

    # Un-check some squares
    driver.find_element_by_id("product:jira:jira-software").click()

    # Weird timing issue in JIRA
    time.sleep(6)

    # Check some squares
    driver.find_element_by_id("sdCheckbox").click()
    time.sleep(1)

update_access('someMigrate')


# Add ORG property key by launching the user admin using Selenium
# ------------------------------------------------------------------------
def update_org(username):

    # user/EditUserProperties
    user_add_org = 'https://janrain.atlassian.net/secure/admin/user/EditUserProperties.jspa?name=%s' % username
    driver.get(user_add_org)

    # Fill in the key and value fields
    user_key_elem = driver.find_element_by_id("user-properties-add-property-key")
    user_key_elem.send_keys("ORG")
    user_value_elem = driver.find_element_by_id("user-properties-add-property-value")
    user_value_elem.send_keys("ORG-####")

    # Submit the form
    user_submit_elem = driver.find_element_by_id("user-properties-add-submit")
    user_submit_elem.send_keys(Keys.RETURN)

    # Assert property added
    table_id = driver.find_element(By.CLASS_NAME, 'aui')
    rows = table_id.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
    for row in rows:
        # Get the columns (all the column 2)
        col = row.find_elements(By.TAG_NAME, "td") #note: index start from 0, 1 is col 2
        print col #prints text from the element

update_org('someMigrate')


# Close the browser
# ------------------------------------------------------------------------
def done():
    # Cleanup
    driver.close()

done()

