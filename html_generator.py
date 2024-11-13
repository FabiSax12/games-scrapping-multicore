import json
from bs4 import BeautifulSoup

def create_html():
    base = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Friki TEC</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

            body {
                font-family: 'Press Start 2P', cursive;
                margin: 0;
                padding: 20px;
                background: radial-gradient(circle at center, #1a1a2e, #16213e, #0f3460);
                color: #fff;
                overflow-x: hidden;
            }

            h1 {
                text-align: center;
                color: #ff2e63;
                font-size: 3em;
                text-shadow: 0 0 8px #ff2e63, 0 0 16px #ff2e63;
                margin: 20px 0;
            }

            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                max-width: 1200px;
                margin: 0 auto;
                gap: 20px;
                padding: 20px;
            }

            .grid-item {
                position: relative;
                background-color: #0f3460;
                border: 2px solid #e94560;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                padding: 15px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }

            .grid-item:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 20px rgba(233, 69, 96, 0.6);
            }

            .grid-item img {
                max-width: 80%;
                height: auto;
                display: block;
                border-radius: 8px;
                margin-top: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }

            .grid-item h2 {
                font-size: 1.2em;
                margin: 15px 0;
                color: #ffde7d;
                text-shadow: 0 0 6px #ffde7d;
            }

            .prices {
                width: 100%;
                margin-top: 15px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                align-items: start;
            }

            .prices a, .htlb p {
                color: #ffde7d;
                text-decoration: none;
                font-weight: bold;
                font-size: .7em;
                transition: color 0.3s ease;
            }

            .prices a:hover, .prices a:focus , .htlb p:hover, .htlb p:focus {
                color: #ff2e63;
                text-shadow: 0 0 8px #ff2e63;
            }

            .hltb {
                width: 100%;
                margin-top: 30px;
                display: flex;
                flex-direction: column;
                gap: 10px;
                align-items: start;
                color: #ffde7d;

                p {
                    font-size: .7em;
                    font-weight: bold;
                    margin: 0;
                }
            }

            .star-score {
                position: absolute;
                top: 2px;
                right: 2px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #333;
                font-weight: bold;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);

                span {
                    position: absolute;
                    top: -6px;
                    z-index: 10;
                }
            }

            svg.star {
                position: absolute;
                z-index: 1;
                fill: #ffd700;
                width: 60px;
                height: 60px;
            }
        </style>
    </head>
    <body>
        <h1>Friki Games</h1>
        <div class="grid-container"></div>
    </body>
    </html>
    """

    soup = BeautifulSoup(base, 'html.parser')

    try:
        with open("results.json", "r") as file:
            results = json.load(file)
            grid_container = soup.find('div', class_='grid-container')

            for result in results:
                grid_item = soup.new_tag('div', attrs={"class": 'grid-item'})
                grid_container.append(grid_item)

                # Agregar el título del juego
                title = soup.new_tag('h2')
                title.string = result['title']
                grid_item.append(title)

                # Agregar la imagen de Amazon si está disponible
                amazon_info = result.get('amazon', None)
                bestbuy_info = result.get('bestbuy', None)
                steam_info = result.get('steam', None)

                if amazon_info and 'img' in amazon_info:
                    img_tag = soup.new_tag('img', src=amazon_info['img'])
                    grid_item.append(img_tag)
                elif bestbuy_info and 'img' in bestbuy_info:
                    img_tag = soup.new_tag('img', src=bestbuy_info['img'])
                    grid_item.append(img_tag)
                elif steam_info and 'img' in steam_info:
                    img_tag = soup.new_tag('img', src=steam_info['img'])
                    grid_item.append(img_tag)
                else:
                    no_image = soup.new_tag('p')
                    no_image.string = "Image not available"
                    grid_item.append(no_image)

                # Puntaje de Metacritic en una estrella amarilla
                metacritic_info = result.get('metacritic', None)
                if metacritic_info and 'score' in metacritic_info:
                    score_tag = soup.new_tag('div', attrs={"class": 'star-score'})
                    star_svg = soup.new_tag('svg', viewBox="0 0 24 24", xmlns="http://www.w3.org/2000/svg", attrs={"class": "star"})
                    star_polygon = soup.new_tag('polygon', points="12,2 15,9 22,9 16,14 18,21 12,17 6,21 8,14 2,9 9,9", fill="#FFD700")
                    star_svg.append(star_polygon)
                    score_tag.append(star_svg)
                    score_span = soup.new_tag('span')
                    score_span.append(metacritic_info['score'])
                    score_tag.append(score_span)
                    grid_item.append(score_tag)

                # Crear la sección de precios e información adicional
                prices_div = soup.new_tag('div', attrs={"class": 'prices'})

                # Enlace y precio de Amazon
                if amazon_info and 'price' in amazon_info:
                    amazon_link = soup.new_tag('a', href=f"https://www.amazon.com/s?k={result['title'].replace(' ', '+')}")
                    amazon_link.string = f"Amazon: ${amazon_info['price']}"
                    prices_div.append(amazon_link)

                # Precio de Best Buy
                if bestbuy_info and 'price' in bestbuy_info:
                    bestbuy_link = soup.new_tag('a', href=f"https://www.bestbuy.com/site/searchpage.jsp?st={result['title'].replace(' ', '+')}")
                    bestbuy_link.string = f"Best Buy: ${bestbuy_info['price']}"
                    prices_div.append(bestbuy_link)

                if steam_info and 'price' in steam_info:
                    steam_link = soup.new_tag(
                        'a',
                        href=f"https://store.steampowered.com/search/?term={result['title'].replace(' ', '+')}"
                    )
                    steam_price_text = f"Steam: {steam_info['price']}"
                    if 'discount' in steam_info and steam_info['discount'] != "No discount":
                        steam_price_text += f" ({steam_info['discount']} off)"

                    steam_link.string = steam_price_text
                    prices_div.append(steam_link)

                # HowLongToBeat
                hltb_div = soup.new_tag('div', attrs={"class": 'hltb'})

                hltb_info = result.get('howlongtobeat', None)
                if hltb_info and 'main_story' in hltb_info:
                    hltb_main = soup.new_tag('p')
                    hltb_main.string = f"Main Story: {hltb_info['main_story']}h"
                    hltb_extra = soup.new_tag('p')
                    hltb_extra.string = f"Main + Extra: {hltb_info['extras']}h"
                    hltb_completionist = soup.new_tag('p')
                    hltb_completionist.string = f"Completionist: {hltb_info['completionist']}h"

                    hltb_div.append(hltb_main)
                    hltb_div.append(hltb_extra)
                    hltb_div.append(hltb_completionist)

                # Agregar la sección de precios e información adicional al grid_item
                grid_item.append(prices_div)
                grid_item.append(hltb_div)

    except FileNotFoundError:
        with open("results.json", "w") as file:
            json.dump([], file)
            create_html()
            return

    # Escribir el archivo HTML final
    with open("index.html", "w") as file:
        file.write(str(soup))

if __name__ == '__main__':
    create_html()
