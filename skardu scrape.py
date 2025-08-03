from selenium import webdriver
from selenium.webdriver.common.by import By
import psycopg2
import time

# Selenium WebDriver
Driver_path = r'C:\Users\ansar\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe'
driver = webdriver.Chrome(executable_path=Driver_path)
driver.get('https://www.booking.com/searchresults.en-gb.html?ss=Skardu&group_adults=2&group_children=0&no_rooms=1')
time.sleep(5)

#  Get hotel links
hotel_elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="title-link"]')
links = [hotel.get_attribute('href') for hotel in hotel_elements]

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="booking_scraper",
    user="postgres",
    password="12345",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Loop through hotel links and extract data
for link in links:
    driver.get(link)
    time.sleep(3)

    try:
        name = driver.find_element(By.CLASS_NAME, 'ddb12f4f86').text
    except:
        name = "Name not found"

    try:
        location_raw = driver.find_element(By.CSS_SELECTOR, 'div.b99b6ef58f.cb4b7a25d9.b06461926f').text
        location = location_raw.split('\n')[0]
    except:
        location = "Location not found"

    try:
        rating = driver.find_element(By.XPATH, '//div[@data-testid="promotional-banner-content-subtitle"]').text.strip()
    except:
        rating = "Rating not found"

    try:
        description = driver.find_element(By.CLASS_NAME, 'f1152bae71').text.strip()
    except:
        description = "Description not found"

    print(f"Hotel: {name}")
    print(f"Location: {location}")
    print(f"Rating: {rating}")
    print(f"Description: {description}")
    print('-' * 40)

    # Insert into database
    cur.execute(
        "INSERT INTO hotels (name, location, rating, description) VALUES (%s, %s, %s, %s)",
        (name, location, rating, description)
    )
    conn.commit()

# Close
cur.close()
conn.close()
driver.quit()
