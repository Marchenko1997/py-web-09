import scrapy
import json


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    quotes = []
    authors_data = {}
    visited_authors = set()

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            quote_text = quote.xpath("span[@class='text']/text()").get()
            author = quote.xpath("span/small[@class='author']/text()").get()
            tags = quote.xpath("div[@class='tags']/a[@class='tag']/text()").getall()

          
            self.quotes.append(
                {"tags": tags, "author": author, "quote": quote_text}  
            )

            author_link = quote.xpath("span/a/@href").get()
            if author_link and author_link not in self.visited_authors:
                self.visited_authors.add(author_link)
                yield response.follow(author_link, callback=self.parse_author)

        next_page = response.xpath("//li[@class='next']/a/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
           
            with open("quotes.json", "w", encoding="utf-8") as f:
                json.dump(self.quotes, f, ensure_ascii=False, indent=2)

            with open("authors.json", "w", encoding="utf-8") as f:
                json.dump(
                    list(self.authors_data.values()), f, ensure_ascii=False, indent=2
                )

    def parse_author(self, response):
        fullname = response.xpath("//h3[@class='author-title']/text()").get().strip()
        born_date = response.xpath("//span[@class='author-born-date']/text()").get()
        born_location = response.xpath(
            "//span[@class='author-born-location']/text()"
        ).get()
        description = (
            response.xpath("//div[@class='author-description']/text()").get().strip()
        )

        self.authors_data[fullname] = {
            "fullname": fullname,
            "born_date": born_date,
            "born_location": born_location,
            "description": description,
        }
