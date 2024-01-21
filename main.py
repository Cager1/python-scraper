from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def webScrape(url):
    chrome_options = FirefoxOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')

    with webdriver.Firefox(options=chrome_options) as driver:
        print('scraping')
        driver.get(url)
        names = driver.find_elements(By.CLASS_NAME, 'main-heading')
        prices = driver.find_elements(By.CLASS_NAME, 'smaller')

        return [name.text for name in names], [price.text for price in prices]


def scrape_all(urls):
    full_names = []
    full_prices = []

    with ThreadPoolExecutor() as executor:
        # Use executor.map to run webScrape concurrently for each URL
        results = list(executor.map(webScrape, urls))

    # Unpack the results into full_names and full_prices
    for names, prices in results:
        full_names.extend(names)
        full_prices.extend(prices)

    return full_names, full_prices


def scraping(urls):
    names, prices = scrape_all(urls)
    macs = {}

    for i in range(len(names)):
        macs[names[i]] = prices[i]

    for key in macs:
        macs[key] = macs[key].replace('KM', '')
        macs[key] = macs[key].replace(' ', '')
        macs[key] = macs[key].replace('.', '')
        macs[key] = macs[key].replace(',', '.')
        # if macs[key] cant be converted to float it is not a price
        try:
            macs[key] = float(macs[key])
        except:
            macs[key] = 0

    most_expensive = max(macs, key=macs.get)
    least_expensive = min(macs, key=macs.get)
    return macs


@app.post("/scrape")
async def root(info: Request):
    data = await info.json()
    # make urls list of items that are url + page number (1-10)
    base_url = data['url']
    urls = [f"{base_url}&page={i}" for i in range(1,2)]
    return scraping(urls)

@app.get("/")
async def root():
    return {"message": "Hello World"}
