import os
from selenium.webdriver.common.by import By
os.environ['PATH'] += r"C:/Selenium_drivers"
from selenium import webdriver
f = open("Search_test_log.txt",'w')

driver = webdriver.Chrome()
driver.get("http://127.0.0.1:8000")
admin_button = driver.find_element(By.XPATH,"//a[text()=\'Manager\']")
admin_button.click()
username_field = driver.find_element(By.NAME,'username')
username_field.send_keys('DAM')
password_field = driver.find_element(By.NAME,'password')
password_field.send_keys('damdamdam')
log_in = driver.find_element(By.XPATH,"//input[@value='Log in']")
log_in.click()
driver.implicitly_wait(5)
books = driver.find_element(By.XPATH,"//a[text()='Books']")
books.click()
table = driver.find_element(By.ID,'result_list')
print(table.text.split('\n'))
book_name = list()
rows = table.find_elements(By.CLASS_NAME,'field-title')
for row in rows:
    book_name.append(row.text)
print(book_name)
driver.close()
book_name = book_name[:10]
for i in book_name:
    driver1 = webdriver.Chrome()
    driver1.get("http://127.0.0.1:8000")
    customer_button = driver1.find_element(By.CLASS_NAME,'btn-primary')
    customer_button.click()
    search_field=  driver1.find_element(By.CLASS_NAME,"form-control")
    t = i
    search_field.clear()
    search_field.send_keys("{}".format(t))
    search_button = driver1.find_element(By.CLASS_NAME,'btn-outline-secondary')
    search_button.click()
    try:
        print(t)
        book_found = driver1.find_element(By.XPATH,"//h6[@class='card-title' and text()='{}']".format(t))
        f.write("{}: Test case Success\n".format(t))

    except:
        f.write("{}: Test case Failed\n".format(t))
    driver1.close()
f.close()
