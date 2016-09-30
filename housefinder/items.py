from scrapy.item import Item, Field


class HouseItem(Item):
    id = Field()
    provider = Field()
    name = Field()
    price = Field()
    rooms = Field()
    meters = Field()
    floor = Field()
    link = Field()
