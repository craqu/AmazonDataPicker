#!/opt/homebrew/bin/python3.9
from urllib.request import urlopen, HTTPHandler
from urllib.request import Request
from bs4 import BeautifulSoup as soup
from os import path
import csv
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'


class Amazon:
    def __init__(self, stdin):
        search = 'https://www.amazon.ca' + f'/s?k={stdin.replace(" ", "+")}'
        print(search)
        self.set_url(search)
        self.data = self.access_data()
        self.price_sorted_data = self.sort_by_price()
        self.ratting_sorted_data = self.sort_by_ratting()

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
            name = name.contents[0].replace(',', '|').split(
                '|')[0].split('—')[0].split('-')[0]
            if len(name.split(' ')) > 12:
                name = ' '.join(name.split(" ")[:11])
            try:
                rating = container.find('i').contents[0].contents[0].split()[
                    0] if container.find('i').contents else 'N/E'
            except(AttributeError):
                rating = 'N/E'
            data.append([name, str(price).replace(',', ''),
                        str(rating).replace(',', '.')])

        return data

    def item2csv(self, name='Test', price=False, ratting=False):
        filename = f"{name}.csv"
        file_exist = path.exists(filename)
        data = self.data
        if price:
            data = self.price_sorted_data
        elif ratting:
            data = self.ratting_sorted_data

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
        res = sorted(data, key=k)
        return res

    def sort_by_ratting(self):
        data = self.access_data()
        res = sorted(data, key=lambda a: float(a[2]))
        return res


a = Amazon("macbook pro")
a.many_pages(2)
a.item2csv("macbook_sorted", price=True)