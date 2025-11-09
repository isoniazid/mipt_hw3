# Библиотеки, которые могут вам понадобиться
# При необходимости расширяйте список
import time
import requests
from bs4 import BeautifulSoup


def get_book_data(book_url: str) -> dict:
    """
    Извлекает информацию о книге из HTML‑страницы по указанному URL.

    Функция выполняет HTTP‑запрос к заданной URL‑ссылке, парсит HTML‑содержимое
    с помощью BeautifulSoup и собирает:
    - данные из таблицы (ключ‑значение по <th>/<td>);
    - название книги (<h1>);
    - описание (блок после <div id="product_description">);
    - рейтинг в звёздах (класс star-rating).

    Args:
        book_url (str): URL‑адрес страницы с информацией о книге.

    Returns:
        result (dict[str, str]): Словарь с полями:
            - все поля из таблицы (UPC, Product Type и т. п.);
            - 'Title' - название книги;
            - 'Description' - описание;
            - 'Rating' - оценка в звёздах.

    Raises:
        requests.Timeout:
            Если запрос превысил установленный таймаут (10 секунд).
        requests.HTTPError:
            Если сервер вернул статус‑код, указывающий на ошибку (4xx, 5xx).
            Вызывается методом `raise_for_status()`.
        requests.RequestException:
            Базовое исключение для всех ошибок библиотеки requests
            (включая соединения, перенаправления и др.).
        Exception:
            Любые другие непредвиденные ошибки (например, при парсинге HTML).
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    rating_map = {
                'One': 1,
                'Two': 2,
                'Three': 3,
                'Four': 4,
                'Five': 5
            }


    result : dict[str,str] = dict()

    html_page : requests.Response = requests.get(book_url, timeout=10)
    html_page.raise_for_status()
    html_page.encoding = 'utf-8'
   
    soup = BeautifulSoup(html_page.text, 'html.parser')
    
    
    prod_info_table = soup.find('table', class_='table table-striped')
    if prod_info_table:
        rows = prod_info_table.find_all('tr')
    
        for row in rows:
            th = row.find('th')
            td = row.find('td')
        
            if th and td:
                key = th.get_text(strip=True)      
                value = td.get_text(strip=True)
                result[key] = value
    
    title_elem = soup.find('h1')
    if title_elem:
        result['Title'] = title_elem.get_text(strip=True)


    desc_div = soup.find('div', id='product_description')
    if desc_div:
        desc_p = desc_div.find_next_sibling('p')
        if desc_p:
            result['Description'] = desc_p.get_text(strip=True)


    rating_p = soup.find('p', class_=lambda c: c and 'star-rating' in c.split())
    if rating_p and 'class' in rating_p.attrs:
        classes = rating_p['class']
        rating_class = [c for c in classes if c != 'star-rating']
        if rating_class:
            result['Rating'] = str(rating_map.get(rating_class[0], ''))

    return result
    # КОНЕЦ ВАШЕГО РЕШЕНИЯ





def scrape_books(starts_from: int, is_save : bool=True) -> list[dict[str, str]]:
    """
    Парсит страницы каталога книг и собирает данные о каждой книге.

    Для каждой книги вызывает get_book_data для получения детальной информации.

    Args:
        starts_from (int): страница, с которой начинается поиск

        is_save (bool): Если True — сохраняет результат в books_data.txt.
        

    Returns:
        list[dict]: Список словарей с данными о книгах.
    """


    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    all_books: list[dict[str, str]] = []

    i = starts_from
    while(True):
        print(f'fetching books from page {i}...')
        response : requests.Response = requests.get(f'https://books.toscrape.com/catalogue/page-{i}.html', timeout=10)
        if(response.status_code == 404):
            print(f'it seems catalogue is finished as page {i} returns 404')
            break
        if(response.status_code != 200):
            print(f'invalid status code for page {i}, continue')
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='product_pod')
        for article in articles:
                # Находим ссылку на страницу книги
            link_elem = article.find('h3').find('a')
            if link_elem and 'href' in link_elem.attrs:
                book_rel_path = link_elem['href']
                # Формируем полный URL
                if book_rel_path.startswith('..'):
                    book_url = "http://books.toscrape.com/" + book_rel_path[3:]
                else:
                    book_url = "http://books.toscrape.com/catalogue/" + book_rel_path

                try:
                    book_data = get_book_data(book_url)
                except Exception as e:
                    print(f'error occured while fetching book data: {e}')
                    book_data = None
                if book_data:  # Если данные получены
                    all_books.append(book_data)
                    print(f'Added book data: {book_data}')

                #чтобы не обиделись на наш дудос
                time.sleep(0.1)
        i+=1

    if is_save:
        try:
            with open('books_data.txt', 'w', encoding='utf-8') as f:
                for book in all_books:
                    f.write(str(book) + '\n')
            print("info saved in books_data.txt")
        except IOError as e:
            print(f"error occured while saving file: {e}")

    return all_books
    # КОНЕЦ ВАШЕГО РЕШЕНИЯ