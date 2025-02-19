import logging
import os
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import NoReturn

import pandas as pd
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_page(logger: logging.Logger, wine_path: str) -> None:
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html']),
    )

    template = env.get_template('template.html')

    template_context = get_template_context(wine_path)
    rendered_page = template.render(**template_context)
    logger.debug(f'{template_context=}')

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


def get_template_context(wine_path: str) -> dict:
    current_year = datetime.now().year
    foundation_year = 1920
    company_age = format_year(current_year - foundation_year)

    file = pd.read_excel(
        wine_path, na_values=['N/A', 'NA'], keep_default_na=False
    )
    products = file.to_dict(orient='records')
    products_by_types = defaultdict(list)

    for product in products:
        default_type = 'Напитки'
        product_type = product['Категория'] or default_type
        products_by_types[product_type].append(product)

    return {
        'company_age': company_age,
        'products_by_types': products_by_types,
    }


def format_year(year: int) -> str:
    if 4 < year % 100 < 21:
        return f'{year} лет'

    last_number = year % 10
    if last_number == 1:
        return f'{year} год'
    elif 2 <= last_number <= 4:
        return f'{year} года'
    else:
        return f'{year} лет'


def main() -> NoReturn:
    load_dotenv()
    wine_path = os.environ['WINE_PATH']
    log_level = os.getenv('LOG_LEVEL', 'INFO')

    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)

    render_page(logger=logger, wine_path=wine_path)

    logger.info('Запускаю сервер..')
    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
