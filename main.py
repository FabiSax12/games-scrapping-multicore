from bs4 import BeautifulSoup
from multiprocessing import Pool
from html_generator import create_html
import requests as req
import time
import csv
import json

# Constants
URL_METACRITIC = "https://www.metacritic.com"
URL_STEAM = "https://store.steampowered.com"
URL_AMAZON = "https://www.amazon.com"

def scrape_amazon_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        search_title = title.replace(' ', '+')
        amazon_url = f"{URL_AMAZON}/s?k={search_title}&i=videogames"

        response = req.get(amazon_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('div', {'data-index': 2})

        if product:
            product_image = product.find("img", {"class", "s-image"})
            product_title = product.find("span", {"class", "a-size-medium a-color-base a-text-normal"})

            if product_image:
                product_image = product_image['src']

            if product_title:
                product_title = product_title.text

            return {"title": title, "amazon": {"title": product_title, "img": product_image} }
        else:
            return {"title": title, "amazon_error": "Product not found"}

    except req.RequestException as e:
        return {"title": title, "amazon_error": str(e)}

def scrape_steam_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        search_title = title.replace(' ', '+')
        steam_url = f"{URL_STEAM}/search/?term={search_title}"

        response = req.get(steam_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('a', {'class': 'search_result_row'})

        if product:
            product_image = product.find("img")['src']
            product_title = product.find("span", {'class': 'title'}).text

            return {"title": title, "steam": {"title": product_title, "img": product_image} }
        else:
            return {"title": title, "steam_error": "Product not found"}

    except req.RequestException as e:
        return {"title": title, "steam_error": str(e)}

def scrape_metacritic_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        search_title = title.replace(' ', '-').lower().replace(':', '')
        metacritic_url = f"{URL_METACRITIC}/game/{search_title}"

        response = req.get(metacritic_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('li', {'class': 'result'})

        if product:
            # Todo - Extract metacritic data

            return {"title": title, "metacritic": {} }
        else:
            return {"title": title, "metacritic_error": "Game not found"}

    except req.RequestException as e:
        return {"title": title, "metacritic_error": str(e)}

def run_parallel_scraping(titles: list[str]) -> list[dict]:
    with Pool(8) as pool:
        print("Starting scraping...")
        results = pool.map(scrape_all_sources, titles)

        with open("results.json", "w") as file:
            json.dump(results, file)

        print("Scraping finished!")

    return results

def scrape_all_sources(title: str) -> dict:
    amazon_data = scrape_amazon_game(title)
    steam_data = scrape_steam_game(title)
    metacritic_data = scrape_metacritic_game(title)

    combined_data = {
        "title": title,
        "amazon": amazon_data.get("amazon", amazon_data.get("amazon_error")),
        "steam": steam_data.get("steam", steam_data.get("steam_error")),
        "metacritic": metacritic_data.get("metacritic", metacritic_data.get("metacritic_error"))
    }

    return combined_data

if __name__ == '__main__':
    titles = []
    scraped_data = []

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


