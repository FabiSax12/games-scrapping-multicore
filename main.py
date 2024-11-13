import os
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from howlongtobeatpy import *
from html_generator import create_html
import requests as req
import time
import csv
import json
import multiprocessing

# Constants
URL_AMAZON = "https://www.amazon.com"
URL_METACRITIC = "https://www.metacritic.com"
URL_BESTBUY = "https://www.bestbuy.com"
URL_WALMART = "https://www.walmart.com"
URL_STEAM = "https://store.steampowered.com"

session = req.Session()
hltb = HowLongToBeat()

def scrape_amazon_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": 'session-id=143-1980534-0337528; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:CR"; ubid-main=134-4428424-6385324; lc-main=es_US; session-token=eAHhEebfZOKNZCFjEtTER7imNeXBtgWZspEFTg0PwjBI2wF5x8pqOJpgvVah9oUN9b/9qKqzc2jzyKpvdT/amshWLCwkemFrRy8YcW+9brHt/siQr69ABNb5/xe+wbnWi25rgKvaCNVAK3qN9HgSoJByzfaLV0WOpkXkAoRp6t8RvE3eL652QO+0dufx9k/VNAK8yjB74sXBhfPmkEmUiQs0HeioPS16GvC86BYzj1lymhFuTv3bYn4bhLoDPfEuv6IM565jD7AU3FbrHVnfiZdB99xsdc6qzpgxcK4EynfCf9G5Yy1auVPyNyMHrew0vA44QudvUgbwXjWowwDhob9AqCYf+PFv; csm-hit=tb:2MS5PR7W54Y5RWQTNEGK+s-D9B0X537AWVCJTGVQ95S|1731309958139&t:1731309958139&adb:adblk_yes'
        }

        search_title = title.replace(' ', '+')
        amazon_url = f"{URL_AMAZON}/s?k={search_title}&i=videogames"

        response = req.get(amazon_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = None
        for i in range(2, 10):
            product = soup.find('div', {'data-index': i})
            if product:
                break

        if product:
            product_image = product.find("img", {"class", "s-image"})
            product_title = product.find("span", {"class", "a-size-medium a-color-base a-text-normal"})
            product_price = product.find("span", {"class", "a-offscreen"})
            product_rating = product.find("span", {"class", "a-icon-alt"})

            if product_image:
                product_image = product_image['src']

            if product_title:
                product_title = product_title.text

            return {
                "title": title,
                "amazon": {
                    "title": product_title,
                    "img": product_image,
                    "price": product_price.text.split("$")[1] if product_price else "Price not available",
                    "rating": product_rating.text if product_rating else "Rating not available"
                }
            }
        else:
            return {"title": title, "amazon_error": "Product not found"}

    except Exception as e:
        return {"title": title, "amazon_error": str(e)}

def scrape_metacritic_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        search_title = title.replace(' ', '-').lower().replace(':', '')
        metacritic_url = f"{URL_METACRITIC}/game/{search_title}"

        response = session.get(metacritic_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        score_div = soup.find('div', {'class': 'c-siteReviewScore'})

        if score_div:
            score = score_div.find("span").get_text()

            return {"title": title, "metacritic": {"score": score} }
        else:
            return {"title": title, "metacritic_error": "Game not found"}

    except Exception as e:
        return {"title": title, "metacritic_error": str(e)}

def scrape_howlongtobeat_game(title: str) -> dict:
    try:
        res = hltb.search(title, SearchModifiers.HIDE_DLC)

        if res is not None and len(res) > 0:
            return {
                "title": title,
                "howlongtobeat": {
                    "main_story": res[0].main_story if res[0].main_story is not None else "Not available",
                    "extras": res[0].main_extra if res[0].main_extra is not None else "Not available",
                    "completionist": res[0].completionist if res[0].completionist is not None else "Not available"
                }
            }
        else:
            return {"title": title, "howlongtobeat_error": "Game not found"}

    except Exception as e:
        print(f"Error: {e}")
        return {"title": title, "howlongtobeat_error": str(e)}

def scrape_bestbuy_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": "rxVisitor=1731208707809OHSHEFM176QV31HTCG3SRD04O8DDVHQK; dtSa=-; bby_rdp=l; SID=aee003a0-24b4-4c9f-904b-d275e661d00d; CTT=bf3a6ea6a0e084754f395351ae1d8498; bby_cbc_lb=p-browse-e; intl_splash=false; intl_splash=false; ltc=%20; vt=0b3ab151-9f15-11ef-bfe8-12fba6a99af5; bm_sz=09BC539923770442A0BD1972703D0F13~YAAQl9XdF8A6SwuTAQAAin8lFBnOgTL/c/pL4Bku72kJt6laMLKqEkZ9mBgqC78p/OYzmjXshj1ovnHmWq8tP5Y7X7DC+V5tHWLSwczv3PMQmxeP5a13NzkguqVMaoo0Yysc+FfA0AEx6EcIomAYXGZRc8Fr9y4IeGoIzj2LzjbPuNZZGL1d/uNVZ6wscBiCt0VQseMJM3VRNBljyX4huBl7o1MaP0+WNYkGSCs6wnkoaLrmuRaSSHSwDCE+6QFtjukEQBQ0noPHhvk+aYjZ2KhRy2Lw8N8pv7Wr6nfzl22wydMGlqjqRDF9x6CHeIAxlPbMNI/OQrKK5tAvf4AeCSb+hjzEjzcHa8VdabG/cyXWl5rbVxLuU5sp3a+TIl1AjCkugTtrdEcg51IubDzyeyj83wGfJkVXOutWmbwiyTk=~4274232~3682871; _abck=74B55FB6D33E0459C4E3BA53B0D7FB9E~0~YAAQl9XdF8c6SwuTAQAAJYAlFAwh0KTpbDu1YGqhCONV7GhJXO8A36esQH8RddmIBQaBOiuFBvApb12ffzPY0QrDM4debBM4bwRejm25zbsq97vNcPzhmjudCgeWWPm4WQ4RO/98bGxuMfvOzjSiY0hGkjdoB28rbTWkp0QY2utwnKT+q0K89SjYdAsgFfdOetIX0569/iiBXvIRnEnOFzop2KYVWSvNNBW0eVdrC4LLKJFpm1QtCXZl4pzGL3z0Jrl3OwRbAdlKAftrnvYe8dF4V4qTo1UmjFQJGYwbs+cGA81D15Y2gdUeFH2cSidD1IA45+Ul5J5oCQYxhC/PIcWHo9KR6HsKAZZ5Dn8jl0wrfvepYmm+/2NI/Dw4sCItpmAurxXJY+5M+Rw6Q32mef2WkCYeTv+ZLBFCVoFIbHPdAwWrtP6Lkv/WOemkVgW84ZX+DvD0XJB+jU4jvpZJeRzzLI+dJQ190oPlR9/ngKGV71pPmx7fJ14Kcf9O0ctqd6db2p97VJQ=~-1~-1~1731213414; lux_uid=173120982237004482; COM_TEST_FIX=2024-11-10T03%3A37%3A03.835Z; dtPC=-80$209822547_390h-vPCFSUTACAHMUHIHEMLQJPRKGPVUJHFSK-0e0; bby_loc_lb=p-loc-e; locDestZip=33040; locStoreId=1178; sc-location-v2=%7B%22meta%22%3A%7B%22CreatedAt%22%3A%222024-11-10T03%3A37%3A04.558Z%22%2C%22ModifiedAt%22%3A%222024-11-10T03%3A37%3A04.645Z%22%2C%22ExpiresAt%22%3A%222025-11-10T03%3A37%3A04.645Z%22%7D%2C%22value%22%3A%22%7B%5C%22physical%5C%22%3A%7B%5C%22zipCode%5C%22%3A%5C%2233040%5C%22%2C%5C%22source%5C%22%3A%5C%22A%5C%22%2C%5C%22captureTime%5C%22%3A%5C%222024-11-10T03%3A37%3A04.558Z%5C%22%7D%2C%5C%22destination%5C%22%3A%7B%5C%22zipCode%5C%22%3A%5C%2233040%5C%22%7D%2C%5C%22store%5C%22%3A%7B%5C%22storeId%5C%22%3A1178%2C%5C%22zipCode%5C%22%3A%5C%2233034%5C%22%2C%5C%22storeHydratedCaptureTime%5C%22%3A%5C%222024-11-10T03%3A37%3A04.644Z%5C%22%7D%7D%22%7D; bby_shpg_lb=p-shpg-e; bby_ispu_lb=p-ispu-e; dtCookie=v_4_srv_8_sn_Q1E0KT9O4PQ482QV084ADP6AMJOCHCS9_app-3A0fc0394d863e8c89_1_ol_0_perc_100000_mul_1; rxvt=1731211630861|1731208707811; blue-assist-banner-shown=true"
        }

        search_title = title.replace(' ', '+')
        bestbuy_url = f"{URL_BESTBUY}/site/searchpage.jsp?qp=category_facet%3DAll%20Video%20Games~pcmcat1487698928729&st={search_title}"

        response = session.get(bestbuy_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')


        product = soup.find('li', {'class': 'sku-item'})

        if product:
            product_price_div = product.find("div", {'class': 'priceView-customer-price'})
            product_price = product_price_div.find("span").text[1:]
            product_img = product.find("img", {'class': 'product-image'})

            if product_img:
                product_img = product_img["src"]


            return {"title": title, "bestbuy": {"price": product_price, "img": product_img} }
        else:
            return {"title": title, "bestbuy_error": "Product not found"}

    except Exception as e:
        return {"title": title, "bestbuy_error": str(e)}

def scrape_walmart_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1"
        }

        search_title = title.replace(' ', '+')
        walmart_url = f"{URL_WALMART}/search?q={search_title}&facet=facet_product_type%3AVideo+Games"

        response = session.get(walmart_url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        print(soup)

        product = soup.find('div', {"class": "sans-serif mid-gray relative flex flex-column w-100 hide-child-opacity"})

        if product:
            product_image = product.find("img", {"data-testid": "productTileImage"})
            product_price_div = product.find("span", {"class": "mr1 mr2-xl b black lh-copy f5 f4-l"})

            if product_image:
                product_image = product_image['src']
            else:
                product_image = "Image not available"

            if product_price_div:
                product_price = product_price_div.text.replace("$", "")
            else:
                product_price = "Price not available"

            return {"title": title, "walmart": {"img": product_image, "price": product_price} }
        else:
            return {"title": title, "walmart_error": "Product not found"}

    except Exception as e:
        return {"title": title, "walmart_error": str(e)}

def scrape_steam_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "wants_mature_content=1; steamCountry=CR%7C7766a1642d661cbc747d8a96600ca0d1; browserid=380085606837331937; sessionid=142d458a40ff9eb0c72c008b; timezoneOffset=-21600,0; birthtime=1108188001; lastagecheckage=12-February-2005; recentapps=%7B%22292030%22%3A1731519057%7D; app_impressions=2300320@1_4_4__118|473930@1_4_4__125|2996040@1_7_15__13|105600@1_7_15__13|2513280@1_7_15__13|440@1_7_15__13|2510960@1_7_15__13|2429640@1_7_15__13|570@1_7_15__13|730@1_7_15__13|3188550@1_7_15__13|1222670@1_7_15__13|2141910@1_7_15__13|1286220@1_7_15__13|271590@1_7_15__13|1845910@1_7_15__13|292030:378649:378648@1_7_15__13|2530490@1_7_15__13|210970@1_7_15__13|20920@1_7_15__13|20900@1_7_15__13|20900@1_5_9__412|20920@1_5_9__412|292030@1_5_9__412"
        }

        search_title = title.replace(' ', '+')
        steam_url = f"{URL_STEAM}/search/?term={search_title}"

        response = req.get(steam_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('a', {'class': 'search_result_row'})

        if product:
            product_title = product.find("span", {'class': 'title'}).text

            print(product_title.lower(), title.lower(), product_title.lower().find(title.lower()))

            if product_title.lower().replace(":", "").find(title.lower().replace(":", "")) == -1:
                return {"title": title, "steam": {"title": product_title, "img": None, "price": "Not found"} }

            product_image = product.find("img")['src']
            product_title = product.find("span", {'class': 'title'}).text
            price = product.find("div", {"class": "discount_final_price"})

            if price:
                price: str = price.text.strip()
                if price != "Free":
                    price = price.replace("₡", "")
                    price = price.replace(".", "")
                    price = price.split(",")[0]
                    if price.isnumeric():
                        price = int(price)
                        price = f"{(price / 530):.2f}"

            return {"title": title, "steam": {"title": product_title, "img": product_image, "price": price} }
        else:
            return {"title": title, "steam_error": "Not found"}

    except Exception as e:
        return {"title": title, "steam_error": str(e)}

def scrape_all_sources(title: str) -> dict:
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_amazon = executor.submit(scrape_amazon_game, title)
        future_bestbuy = executor.submit(scrape_bestbuy_game, title)
        future_steam = executor.submit(scrape_steam_game, title)

        future_metacritic = executor.submit(scrape_metacritic_game, title)
        # future_howlongtobeat = executor.submit(scrape_howlongtobeat_game, title)

        amazon_data = future_amazon.result()
        bestbuy_data = future_bestbuy.result()
        steam_data = future_steam.result()

        metacritic_data = future_metacritic.result()
        # howlongtobeat_data = future_howlongtobeat.result()

    combined_data = {
        "title": title,
        "amazon": amazon_data.get("amazon", amazon_data.get("amazon_error")),
        "bestbuy": bestbuy_data.get("bestbuy", bestbuy_data.get("bestbuy_error")),
        "steam": steam_data.get("steam", steam_data.get("steam_error")),
        "metacritic": metacritic_data.get("metacritic", metacritic_data.get("metacritic_error")),
        # "howlongtobeat": howlongtobeat_data.get("howlongtobeat", howlongtobeat_data.get("howlongtobeat_error"))
    }

    return combined_data

def run_parallel_scraping(titles: list[str]) -> list[dict]:
    max_workers = os.cpu_count()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        print("Starting scraping...")
        results = list(executor.map(scrape_all_sources, titles))

    with open("results.json", "w") as file:
        json.dump(results, file)

    print("Scraping finished!")
    return results

if __name__ == '__main__':

    multiprocessing.set_start_method('spawn')

    while(True):
        titles = []

        with open("games.csv") as file:
            reader = csv.reader(file)
            titles = [row[0] for row in reader]
            titles.pop(0)

        print(f"Scraping {len(titles)} games...")

        start_t = time.time()
        scraped_data = run_parallel_scraping(titles)
        end_t = time.time()

        print(f"Scraping took {(end_t - start_t):.2f} seconds")

        create_html()

        time.sleep(80)

