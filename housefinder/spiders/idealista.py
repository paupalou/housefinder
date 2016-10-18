import scrapy
from housefinder.items import HouseItem


class IdealistaSpider(scrapy.Spider):
    name = 'idealista'
    page_counter = 1
    limit = 50
    HOST = 'http://www.idealista.com'
    start_urls = [
        HOST+'/alquiler-viviendas/palma-de-mallorca-balears-illes/'
    ]

    def text(self, container, rule):
        try:
            return container.xpath(rule+'/text()').extract_first().strip()
        except AttributeError:
            return ''

    def exists_next_page(self, page):
        self.page_counter += 1
        return len(page.xpath('//li[@class="next"]')) > 0

    def create_item(self, house):
        info = house.css('.item-info-container')

        item = HouseItem()
        item['id'] = house.xpath('div/@data-adid').extract_first()
        item['provider'] = 'idealista'
        item['name'] = self.text(info, 'a')
        item['price'] = self.text(info, './/span[@class="item-price"]')
        item['rooms'] = self.text(info, 'span[@class="item-detail"][1]')
        item['meters'] = self.text(info, 'span[@class="item-detail"][2]')
        item['floor'] = self.text(info, 'span[@class="item-detail"][3]')
        item['link'] = "https://www.idealista.com/inmueble/{}/".format(
            item['id']
        )

        return item

    def parse(self, response):
        main = response.xpath('//div[@id="main-content"]').css(
                '.items-container'
                )
        houses = main.xpath('.//article[not(@class)]')

        for house in houses:
            yield self.create_item(house)

        if self.page_counter < self.limit and self.exists_next_page(response):
            next_page_anchor = response.xpath('//li[@class="next"]/a/@href')
            next_page = response.urljoin(next_page_anchor.extract_first())
            yield scrapy.Request(next_page, callback=self.parse)
