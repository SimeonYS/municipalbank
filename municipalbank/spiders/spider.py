import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import MunicipalbankItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class MunicipalbankSpider(scrapy.Spider):
	name = 'municipalbank'
	start_urls = ['https://www.municipalbank.bg/displaybg.aspx?page=news&showArchive=yes']

	def parse(self, response):
		post_links = response.xpath('//div[@class="archive"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_links)

	def parse_links(self, response):
		links = response.xpath('//span[@class="title-p"]/a/@href').getall()
		yield from response.follow_all(links, self.parse_post)


	def parse_post(self, response):

		date = response.xpath('//span[@class="date"]/text()').get()
		title = response.xpath('//p[@class="NewsTitle"]/strong/text()').get()
		content = response.xpath('//span[@id="page_text"]/p//text()[not (ancestor::p[@class="NewsTitle"])]').getall()
		if not content:
			content = response.xpath('//span[@id="page_text"]/p//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=MunicipalbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
