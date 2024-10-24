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
        <title>Scraped Data</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            .grid-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 20px;
            }
            .grid-item {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                text-align: center;
                transition: transform 0.3s ease;
            }
            .grid-item:hover {
                transform: scale(1.05);
            }
            .grid-item img {
                max-width: 100%;
                height: auto;
                display: block;
            }
            .grid-item h2 {
                font-size: 18px;
                margin: 15px 0;
                color: #555;
            }
            .grid-item a {
                text-decoration: none;
                color: #0073e6;
            }
            .grid-item a:hover {
                color: #005bb5;
            }
        </style>
    </head>
    <body>
        <h1>Scraped Data</h1>
        <div class="grid-container"></div>
    </body>
    </html>
    """

    soup = BeautifulSoup(base, 'html.parser')

    # Cargar los resultados usando json.load()
    try:
        with open("results.json", "r") as file:
            results = json.load(file)
            grid_container = soup.find('div', class_='grid-container')

            for result in results:
                grid_item = soup.new_tag('div', class_='grid-item')
                grid_container.append(grid_item)

                # Agregar el título del juego
                title = soup.new_tag('h2')
                title.string = result['title']
                grid_item.append(title)

                # Agregar la imagen de Amazon (si está disponible) y hacerla un enlace al producto
                amazon_info = result.get('amazon', None)
                steam_info = result.get('steam', None)
                if isinstance(amazon_info, dict) and 'img' in amazon_info:
                    # Crear enlace a Amazon
                    amazon_link = soup.new_tag('a', href=f"https://www.amazon.com/s?k={result['title'].replace(' ', '+')}")
                    amazon_img = soup.new_tag('img', src=amazon_info['img'])
                    amazon_link.append(amazon_img)
                    grid_item.append(amazon_link)
                elif isinstance(steam_info, dict) and 'img' in steam_info:
                    # Crear enlace a Steam
                    steam_link = soup.new_tag('a', href=f"https://store.steampowered.com/search/?term={result['title'].replace(' ', '+')}")
                    steam_img = soup.new_tag('img', src=steam_info['img'])
                    steam_link.append(steam_img)
                    grid_item.append(steam_link)
                else:
                    no_image = soup.new_tag('p')
                    no_image.string = "Image not available"
                    grid_item.append(no_image)
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
