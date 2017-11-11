from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import json
import time
import signal

with open("fips2zip.json") as data_file:
    fips2zip = json.load(data_file)

with open("allfips.txt") as txt_file:
    content = txt_file.readlines()

allfips = [x.strip() for x in content]

fips2precip = {}

starturl = "https://www.wunderground.com/history/"

ua_string = "Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko)"

xpaths = {
    'zipbox': '//*[@id="histSearch"]',
    'submitBtn': '/html/body/div[1]/div[2]/section/div/div[1]/form/input[5]',
    'prevDay': '/html/body/div[1]/div[2]/section/div/div[5]/div[1]/div[1]/div[3]/a',
    'precipInInches': '/html/body/div[1]/div[2]/section/div/div[5]/div[1]/table[1]/tbody/tr[14]/td[2]/span/span[1]'
}

profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", ua_string)
driver = webdriver.Firefox(profile)

def writeToJson(data):
    with open("f2p.json", "w") as json_file:
        json.dump(data, json_file)

def send(xpath, value):
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print ("Couldn't find element specified by xpath: {x}".format(x=xpath))
        return False
    elem.send_keys(value)
    return True

def click(xpath):
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print ("Couldn't find element specified by xpath: {x}".format(x=xpath))
        return False
    elem.click()
    return True

def clear(xpath):
    try:
        elem = driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        print ("Couldn't find element specified by xpath: {x}".format(x=xpath))
        return True
    elem.clear()
    return False

for fips in allfips:
    driver.get(starturl)
    time.sleep(2)
    zipcode = fips2zip[fips]
    send(xpaths['zipbox'], zipcode)
    if not click(xpaths['submitBtn']):
        continue
    time.sleep(3)
    if not click(xpaths['prevDay']):
        continue
    time.sleep(3)
    precip = ""
    try:
        precip_label_elems = driver.find_elements_by_css_selector('td.indent>span')
        precip_label_elem = None
        for e in precip_label_elems:
            if "Precipitation" in e.text:
                precip_elem = e.find_element_by_xpath('./../../td//span[@class="wx-value"]')
                precip = precip_elem.text
    except NoSuchElementException:
        print ("Couldn't find precipitation for zipcode: {z}".format(z=zipcode))

    fips2precip[fips] = precip
    print("Writing to output file...")
    writeToJson(fips2precip)
