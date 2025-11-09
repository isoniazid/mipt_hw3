from bs4 import BeautifulSoup
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_book_data, scrape_books


# --- Тесты для get_book_data ---

def test_get_book_data_returns_dict():
    """Проверяет, что функция возвращает словарь."""
    result = get_book_data("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
    assert isinstance(result, dict)



def test_get_book_data_contains_required_keys():
    """Проверяет наличие обязательных ключей в результате."""
    result = get_book_data("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")

    required_keys = ['Title', 'Description', 'Rating', 'UPC']
    for key in required_keys:
        assert key in result, f"Ключ {key} отсутствует в результате"



def test_get_book_data_title_is_not_empty():
    """Проверяет, что название книги не пустое."""
    result = get_book_data("https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
    assert 'Title' in result
    assert len(result['Title'].strip()) > 0
    assert result['Title'].strip() == "A Light in the Attic"



# --- Тесты для scrape_books ---
def test_scrape_books_returns_list_of_dicts():
    """Проверяет, что scrape_books возвращает список словарей."""
    result = scrape_books(starts_from=50, is_save=False)

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)
    assert len(result) >= 1


def test_scrape_books_collects_correct_number_of_books():
    """Проверяет, что количество книг соответствует числу <article> на странице."""

    response : requests.Response = requests.get(f'https://books.toscrape.com/catalogue/page-{50}.html', timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article', class_='product_pod')


    result = scrape_books(starts_from=50, is_save=False)
    assert len(result) == articles.__len__()  # N article → N книги



def test_scrape_books_stops_on_404():
    """Проверяет, что scrape_books возвращает пустой словарь, если страница не найдена"""
    PAGE_ID = -10000
    result = scrape_books(starts_from=-10000, is_save=False)

    # Должна быть обработана только первая страница
    assert len(result) == 0