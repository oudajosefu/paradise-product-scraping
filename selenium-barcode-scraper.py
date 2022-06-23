from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as sel_exc
import pandas as pd
from time import sleep

CHROMEDRIVER_PATH = '/path/to/chromedriver'
options = Options()
options.headless = True
chromeBrowser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

datasetLocation = '/path/to/list_of_barcodes.csv'

# For excel:
# df = pd.read_excel(datasetLocation, 'Sheet1')

# For csv:
df = pd.read_csv(datasetLocation)

dfNA = df.isna()

error_count = 0
sleep_time = 2

headers = {
    'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,ja;q=0.8,fr;q=0.7',
    'cache-control': 'no-cache'
}

def search(url, browser):
    try:
        browser.get(url)
        if 'did not match any image results' in browser.page_source:
            return 'continue'
        else:
            result = find_image(0, url, browser)
            if result is None:
                return 'continue'
            else:
                return result
                
    except Exception as e:
        global error_count
        error_count += 1
        print(e)
        browser.quit()
        chromeBrowser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)
        sleep(sleep_time * 0.5)
        search(url, chromeBrowser)

def find_image(index, url, browser):
    if not browser.find_elements_by_xpath("//div[@class='Rn1jbe hieTTe']/div[@class='gY8Fyc']/div[@class='c76k3e']/span[@class='vRPqZd']"):
        browser.get(url + '#imgrc=' + browser.find_elements_by_xpath("//div[@jsname='N9Xkfe']")[index].get_attribute('data-id'))
    else:
        browser.get(url + '#imgrc=' + browser.find_elements_by_xpath("//div[@class='tmS4cc jpaVhe XgOJmc']//div[@jsname='N9Xkfe']")[index].get_attribute('data-id'))

    sleep(sleep_time)
    img = browser.find_element_by_xpath("//div[@class='tvh9oe BIB1wf']//div[@class='OUZ5W']/div[@class='zjoqD']/div[@class='qdnLaf isv-id']/div[@class='v4dQwb']/a[@role='link']/img[@class='n3VNCb']").get_attribute('src')
    if 'http' in img and 'data' not in img:
        return img
    else:
        return find_image(index+1, url, browser)

for x in range(0, len(df.index)):
    if dfNA.loc[x, 'Image URL']:
        barcode_name = df.loc[x, 'Handle']
        print(barcode_name)
        src = search('https://www.google.com/search?tbm=isch&q=%s' % barcode_name, chromeBrowser)
        if src == 'continue':
            continue
        print(src)
        df.loc[x, 'Image URL'] = src

        # For excel:
        # df.to_excel(datasetLocation, index=False)

        # For csv:
        df.to_csv(datasetLocation, index=False)
        print('Image inserted.')

print('%i errors.' % error_count)
chromeBrowser.close()
