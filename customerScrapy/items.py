# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CustomerscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass


# 行业分类
class TypeItem(scrapy.Item):
    # 网站的标题
    id = scrapy.Field()
    name = scrapy.Field()
    en_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()


# 行业大分类
class CategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    en_name = scrapy.Field()
    link = scrapy.Field()
    type_id = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()


# 行业细分分类
class IndustryItem(scrapy.Item):
    id = scrapy.Field()
    cat_id = scrapy.Field()
    name = scrapy.Field()
    en_name = scrapy.Field()
    link = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
