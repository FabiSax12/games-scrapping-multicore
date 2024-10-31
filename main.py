import os
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from html_generator import create_html
import requests as req
import time
import csv
import json
import multiprocessing

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

        response = req.get(amazon_url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('div', {'data-index': 2})

        print("Amazon scrapping: ", title)

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

    except Exception as e:
        return {"title": title, "amazon_error": str(e)}

def scrape_steam_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        search_title = title.replace(' ', '+')
        steam_url = f"{URL_STEAM}/search/?term={search_title}"

        response = req.get(steam_url, headers=headers, timeout=5)
        response.raise_for_status()

        print("Steam scrapping: ", title)

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('a', {'class': 'search_result_row'})

        if product:
            product_image = product.find("img")['src']
            product_title = product.find("span", {'class': 'title'}).text

            return {"title": title, "steam": {"title": product_title, "img": product_image} }
        else:
            return {"title": title, "steam_error": "Product not found"}

    except Exception as e:
        return {"title": title, "steam_error": str(e)}

def scrape_metacritic_game(title: str) -> dict:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }

        search_title = title.replace(' ', '-').lower().replace(':', '')
        metacritic_url = f"{URL_METACRITIC}/game/{search_title}"

        response = req.get(metacritic_url, headers=headers, timeout=5)
        response.raise_for_status()

        print("Metacritic scrapping: ", title)

        soup = BeautifulSoup(response.content, 'html.parser')

        product = soup.find('li', {'class': 'result'})

        if product:
            # Todo - Extract metacritic data

            return {"title": title, "metacritic": {} }
        else:
            return {"title": title, "metacritic_error": "Game not found"}

    except Exception as e:
        return {"title": title, "metacritic_error": str(e)}

def scrape_all_sources(title: str) -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_amazon = executor.submit(scrape_amazon_game, title)
        future_steam = executor.submit(scrape_steam_game, title)
        future_metacritic = executor.submit(scrape_metacritic_game, title)

        amazon_data = future_amazon.result()
        steam_data = future_steam.result()
        metacritic_data = future_metacritic.result()

    combined_data = {
        "title": title,
        "amazon": amazon_data.get("amazon", amazon_data.get("amazon_error")),
        "steam": steam_data.get("steam", steam_data.get("steam_error")),
        "metacritic": metacritic_data.get("metacritic", metacritic_data.get("metacritic_error"))
    }

    return combined_data

def run_parallel_scraping(titles: list[str]) -> list[dict]:
    max_workers = os.cpu_count()  # Optimiza según tu CPU
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        print("Starting scraping...")
        results = list(executor.map(scrape_all_sources, titles))

    with open("results.json", "w") as file:
        json.dump(results, file)

    print("Scraping finished!")
    return results

if __name__ == '__main__':
    while(True):
        multiprocessing.set_start_method('spawn')  # Establece el método de inicio a 'spawn'
        titles = []

        with open("games.csv") as file:
            reader = csv.reader(file)
            titles = [row[0] for row in reader]
            titles.pop(0)  # Si tienes un encabezado en tu CSV

        print(f"Scraping {len(titles)} games...")

        start_t = time.time()
        scraped_data = run_parallel_scraping(titles)
        end_t = time.time()

        print(f"Scraping took {(end_t - start_t):.2f} seconds")

        create_html()

        time.sleep(600)

