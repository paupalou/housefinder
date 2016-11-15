import re

from scrapy import Spider, Request
from housefinder.items import HouseItem
from housefinder.config import Provider


class Provider2Spider(Spider):
    provider = Provider(2)
    name = provider.get('name')
    allowed_domains = [provider.get('allowed_domain')]
    HOST = provider.get('host')
    page_counter = 1

    def start_requests(self):
        yield Request(self.provider.get('start_url'), self.parse)

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
        item['provider'] = self.name
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

        if self.exists_next_page(response):
            next_page_anchor = response.xpath(
                    '//li[@class="pagination-next"]/a/@href'
                    )
            next_page = response.urljoin(next_page_anchor.extract_first())
            yield Request(next_page, callback=self.parse)
