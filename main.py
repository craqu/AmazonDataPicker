#!/opt/homebrew/bin/python3.9
from urllib.request import urlopen
from urllib.request import Request
from bs4 import BeautifulSoup as soup
from os import path
from time import sleep
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'


class Amazon:
    def __init__(self, stdin):
        search = 'https://www.amazon.ca' + f'/s?k={stdin.replace(" ", "+")}'
        print(search)
        self.set_url(search)
        self.data = self.access_data()
        print(self.data)
        self.price_sorted_data = self.sort_by_price()
        self.rating_sorted_data = self.sort_by_rating()

    def set_url(self, url):
        self.hostname = 'https://www.amazon.ca'
        req = Request(url, data=None, headers={'User-Agent': f"{user_agent}"})
        client = urlopen(req)
        page_html = client.read()
        client.close()
        page_soup = soup(page_html, "html.parser")
        url_container = page_soup.find(
            'div', {
                'class', 's-widget-container s-spacing-medium s-widget-container-height-medium celwidget slot=MAIN template=PAGINATION widgetId=pagination-button'})
        self.next_url = url_container.find(
            'a', {
                'class', 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})
        self._containers = page_soup.findAll(
            'div', {"class", "a-section a-spacing-base"})

    def access_data(self):
        data = []
        for container in self._containers:
            price_int = container.find('span', {"class", "a-price-whole"})
            name = container.find(
                'span', {'class', 'a-size-base-plus a-color-base a-text-normal'})
            price = price_int.contents[0] if price_int else 0
            name = name.contents[0].replace(',', '|')
            if len(name.split(' ')) > 14:
                name = ' '.join(name.split(" ")[:11])
            try:
                rating = container.find('i').contents[0].contents[0].split()[
                    0] if container.find('i').contents else 'N/E'
            except(AttributeError):
                rating = 'N/E'
            data.append([name, str(price).replace(',', ''),
                        str(rating).replace(',', '.')])

        return data

    def item2csv(self, name='Test', price=False, rating=False):
        filename = f"{name}.csv"
        file_exist = path.exists(filename)
        data = self.data
        if price:
            data = self.price_sorted_data
        elif rating:
            data = self.rating_sorted_data

        with open(filename, 'a') as f:
            if not file_exist:
                f.writelines("name, price, rating")

            for object in data:
                f.writelines("\n" + ",".join(object))

    def next_page(self):
        self.set_url(self.hostname + self.next_url.attrs['href'])

    def many_pages(self, nb):
        self.data = []
        for i in range(nb):
            self.data.append(self.access_data())
            if i != nb - 1:
                print(i + 1)
                try:
                    self.next_page()
                except(AttributeError):
                    print("no more available pages")
                    break

    def sort_by_price(self):
        data = self.data
        def k(a): return int(a[1])
        res = sorted(data, key=k, reverse=True)
        def b(a): return [a[0],str(a[1]),a[2]]
        res = list(map(b, res))
        print(res)
        return res

    def sort_by_rating(self):
        data = self.access_data()
        for index, item in enumerate(data):
            try:
                data[index][2] = float(item[2])
            except(ValueError):
                data[index][2] = 0

        def k(a): return float(a[2])
        res = sorted(data, key=k, reverse=True)
        def b(a): return [a[0], a[1], str(a[2])]
        res = map(b, res)
        def g(a): return [a[0], a[1], 'N/E'] if a[2] == '0' else a
        res = map(g, res)
        return res


if __name__ == "__main__":
    # exemple
    a = Amazon("macbook pro")  # nom de l'item qu'on recherche
    #a.many_pages(1)  # deux pages de data
    # création du fichier csv nommé 'macbook_sorted' trié en fonction du rating
    sleep(1)
    a.item2csv("macbook", price=True)
