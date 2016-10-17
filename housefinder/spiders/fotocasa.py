import scrapy
import re
from housefinder.items import HouseItem


class FotocasaSpider(scrapy.Spider):
    name = 'fotocasa'
    allowed_domains = ['fotocasa.es']
    HOST = 'http://www.fotocasa.es/'
    page_counter = 1
    limit = 25

    def start_requests(self):
        querystring = '?opi=36&ts=Mallorca%20&l=724,4,7,223,0,0,0,0,0'
        querystring += 'bti=2&tti=3&mode=1&cu=es-es'
        url = self.HOST+'/search/results.aspx'+querystring
        yield scrapy.Request(url, self.parse)

    def exists_next_page(self, page):
        self.page_counter += 1
        return len(page.xpath('//li[@class="pagination-next"]')) > 0

    def text(self, container, rule):
        try:
            text = container.xpath('.//span['+rule+']/text()')
            return text.extract_first().strip()
        except AttributeError:
            return ''

    def create_item(self, house):

        def _get_info():
            info = house.xpath('.//span[contains(@id, "_info")]/text()')
            floor = info.extract_first().split(',')[0]

            meters = re.compile(r'(\d+)m')
            findmeters = meters.findall(info.extract_first())
            if not findmeters:
                findmeters = 0
            else:
                findmeters = findmeters.pop()

            rooms = re.compile(r'(\d+) hab')
            findrooms = rooms.findall(info.extract_first())
            if not findrooms:
                findrooms = 0
            else:
                findrooms = findrooms.pop()

            return (floor, findmeters, findrooms)

        def _get_id():
            hid = house.xpath('.//a[contains(@id, "_lnkDetail")]/@propertyid')
            return hid.extract().pop()

        def _get_link():
            anchor = house.xpath('.//a[contains(@id, "_lnkDetail")]/@href')
            return anchor.extract().pop()

        def _get_price():
            price = house.xpath('.//span[contains(@id, "_price")]/text()')
            pricefinder = re.compile(r'(\d+.\d+).*')
            return pricefinder.findall(price.extract_first()).pop()

        item = HouseItem()
        house_info = _get_info()
        item['id'] = _get_id()
        item['link'] = _get_link()
        item['provider'] = 'fotocasa'
        item['name'] = self.text(house, 'contains(@id, "ubication")')
        item['floor'] = house_info[0]
        item['meters'] = house_info[1]
        item['rooms'] = house_info[2]

        item['price'] = _get_price()

        return item

    def parse(self, response):
        house_boxes = response.xpath('//div[@data-id="property-information"]')

        for house in house_boxes:
            yield self.create_item(house)

        if self.page_counter < self.limit and self.exists_next_page(response):
            next_page_anchor = response.xpath(
                    '//li[@class="pagination-next"]/a/@href'
                    )
            next_page = response.urljoin(next_page_anchor.extract_first())
            yield scrapy.Request(next_page, callback=self.parse)
