import scrapy
import logging
import os
import json


class JobScraperSpider(scrapy.Spider):
    name = "job_scraper"
    allowed_domains = ["linkedin.com"]
    total_jobs = 0
    counter_job_based_on_scraped = 0
    counter = 0
    allowed_to_continue = True

    def __init__(self, *args, **kwargs):
        super(JobScraperSpider, self).__init__(*args, **kwargs)

        config_file = os.path.join(os.getcwd(), "config.json")
        with open(config_file, "r") as f:
            self.config = json.load(f)

        self.country_name = kwargs.get("country")
        self.period = kwargs.get("period")

        if self.country_name:
            selected_country = next(
                (
                    country
                    for country in self.config["countries"]
                    if country["name"].lower() == self.country_name.lower()
                ),
                None,
            )
            if selected_country:
                self.geo_id = selected_country["geo_id"]
                self.country_name = selected_country["name"]
            else:
                raise ValueError(
                    f"Country '{self.country_name}' not found in configuration."
                )
        else:
            raise ValueError("The 'country' argument must be specified.")

        if self.period not in self.config["periods"]:
            raise ValueError(f"Period '{self.period}' not found in configuration.")
        self.period_code = self.config["periods"][self.period]

        self.user_agent = self.config.get("user_agent", "default-user-agent")

        self.base_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location={self.country_name}&geoId={self.geo_id}&f_TPR={self.period_code}&trk=public_jobs_jobs-search-bar_search-submit&start={self.counter}&original_referer="
        self.next_page_url_job_listing = self.base_url

    def start_requests(self):
        yield scrapy.Request(
            url=self.base_url,
            callback=self.parse,
            headers={"User-Agent": self.user_agent},
        )

    def parse(self, response):
        urls = response.xpath("//li/div/a/@href").getall()
        for url in urls:
            try:
                url = url[: url.find("?position")]
                yield response.follow(
                    url=url,
                    callback=self.parse_job,
                    headers={"User-Agent": self.user_agent},
                    dont_filter=True,
                    meta={"job_url": url},
                )
            except:
                logging.log(logging.DEBUG, f"THIS URL CANNOT BE REACHED : {url}")

        self.counter += len(urls)

        self.next_page_url_job_listing = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=&location={self.country_name}&geoId={self.geo_id}&f_TPR={self.period_code}&trk=public_jobs_jobs-search-bar_search-submit&start={self.counter}&original_referer="

        if self.next_page_url_job_listing and not (len(urls) == 0 and self.counter == self.counter_job_based_on_scraped):
            try:
                yield response.follow(
                    url=self.next_page_url_job_listing,
                    callback=self.parse,
                    headers={"User-Agent": self.user_agent},
                    dont_filter=True,
                )
            except:
                logging.log(logging.DEBUG, "SOMETHING HAS GONE WRONG")

    def parse_job(self, response):
        title = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/section[contains(@class, "top-card-layout")]/div/div[contains(@class, "entity-info-container")]/div/h1/text()'
        ).get()
        company = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/section[contains(@class, "top-card-layout")]/div/div[contains(@class, "entity-info-container")]/div/h4/div[1]/span[@class="topcard__flavor"]/a/text()'
        ).get()
        location = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/section[contains(@class, "top-card-layout")]/div/div[contains(@class, "entity-info-container")]/div/h4/div[1]/span[contains(@class, "bullet")]/text()'
        ).get()
        time_ago = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/section[contains(@class, "top-card-layout")]/div/div[contains(@class, "entity-info-container")]/div/h4/div[2]/span[contains(@class, "posted-time-ago")]/text()'
        ).get()
        seniority_level = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/div[contains(@class, "details")]/section[contains(@class, "description")]/div/ul/li[1]/span/text()'
        ).get()
        employment_type = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/div[contains(@class, "details")]/section[contains(@class, "description")]/div/ul/li[2]/span/text()'
        ).get()
        job_function = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/div[contains(@class, "details")]/section[contains(@class, "description")]/div/ul/li[3]/span/text()'
        ).get()
        industries = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div/div[contains(@class, "details")]/section[contains(@class, "description")]/div/ul/li[4]/span/text()'
        ).get()
        description = response.xpath(
            './/main/section[contains(@class, "core-rail")]/div[contains(@class, "details")]/div[contains(@class, "details")]/section[contains(@class, "description")]/div[contains(@class, "core-section-container")]/div[contains(@class, "description")]/section/div'
        ).get()
        if title is None:
            logging.log(
                logging.DEBUG,
                f"THIS PAGE IS NOT LOADING PROPERLY, RELOADING: {response.meta['job_url']}",
            )
            yield response.follow(
                url=response.meta["job_url"],
                callback=self.parse_job,
                headers={"User-Agent": self.user_agent},
                dont_filter=True,
                meta={"job_url": response.meta["job_url"]},
            )
            return
        self.counter_job_based_on_scraped += 1

        yield {
            "title": title,
            "company": company,
            "location": location,
            "request_location": self.country_name,
            "date_posted": time_ago,
            "seniorty_level": seniority_level,
            "employment_type": employment_type,
            "job_function": job_function,
            "industries": industries,
            "description": description,
            "job_url": response.meta["job_url"],
        }
