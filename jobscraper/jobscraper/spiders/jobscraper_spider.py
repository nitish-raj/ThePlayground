import scrapy
from jobscraper.items import JobItem

class UpworkSpider(scrapy.Spider):
    name = 'upwork'
    allowed_domains = ['www.upwork.com']
    start_urls = ['https://www.upwork.com/search/jobs/']

    def parse(self, response):
        job_listings = response.css('section.up-card-section')
        
        for job in job_listings:
            item = JobItem()
            item['title'] = job.css('a.job-title-link::text').get().strip()
            item['description'] = job.css('span.job-description::text').get().strip()
            item['budget'] = job.css('span.js-budget::text').get()
            item['posted_time'] = job.css('span.job-posted-time::text').get().strip()
            item['skills'] = job.css('span.skill-label::text').getall()
            
            yield item

        next_page = response.css('button[data-test="pagination-next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)