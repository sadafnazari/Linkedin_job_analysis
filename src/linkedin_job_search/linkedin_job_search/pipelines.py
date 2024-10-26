import sqlite3
import datetime
from bs4 import BeautifulSoup
import os
import pandas as pd
import unicodedata

class LinkedinJobSearchPipeline:
    def process_item(self, item, spider):
        item["title"] = (
            item["title"].strip().replace("\n", "").replace(",", "").strip()
            if item["title"]
            else ""
        )
        item["company"] = (
            item["company"].strip().replace("\n", "").replace(",", "").strip()
            if item["company"]
            else ""
        )
        item["location"] = (
            item["location"].strip().replace("\n", "").replace(",", "").strip()
            if item["location"]
            else ""
        )
        item["city"], item["region"], item["country"] = self.normalize_location(item["location"], item["request_location"])
        item["date_posted"] = (
            item["date_posted"].strip().replace("\n", "").replace(",", "").strip()
            if item["date_posted"]
            else ""
        )
        item["date_posted"] = self.normalize_date(item["date_posted"])
        item["seniorty_level"] = (
            item["seniorty_level"].strip().replace("\n", "").replace(",", "").strip()
            if item["seniorty_level"]
            else ""
        )
        item["employment_type"] = (
            item["employment_type"].strip().replace("\n", "").replace(",", "").strip()
            if item["employment_type"]
            else ""
        )
        item["job_function"] = (
            item["job_function"].strip().replace("\n", "").replace(",", "").strip()
            if item["job_function"]
            else ""
        )
        item["industries"] = (
            item["industries"].strip().replace("\n", "").replace(",", "").strip()
            if item["industries"]
            else ""
        )
        item["description"] = self.normalize_description(item["description"])

        return item

    def normalize_date(self, time_ago):
        if "day" in time_ago:
            days = int(time_ago.split()[0])
            date = datetime.datetime.now() - datetime.timedelta(days=days)
        elif "week" in time_ago:
            weeks = int(time_ago.split()[0])
            date = datetime.datetime.now() - datetime.timedelta(weeks=weeks)
        elif "month" in time_ago:
            months = int(time_ago.split()[0])
            date = datetime.datetime.now() - datetime.timedelta(months=months)
        elif "year" in time_ago:
            years = int(time_ago.split()[0])
            date = datetime.datetime.now() - datetime.timedelta(years=years)
        else:
            date = datetime.datetime.now()

        date = date.strftime("%Y-%m-%d %H:%M:%S")

        return date

    def normalize_description(self, description):
        soup = BeautifulSoup(description, "html.parser")

        cleaned_text = soup.get_text(separator=" ", strip=True)

        cleaned_text = " ".join(cleaned_text.split())
        return cleaned_text
    
    def normalize_location(self, location, request_location):
        config_file = os.path.join(os.getcwd(), f'../../resources/cities_and_regions_{request_location}.json')
        cities_and_regions = pd.read_json(config_file)
        location = self.normalize_location_text(location)
        location = location.lower()
        location = location.replace('sub region', '')
        location = location.replace('northen', 'north')
        location = location.replace('southern', 'south')
        location = location.replace('savonia', 'savo')
        location_parts = location.split()
        city_match, region_match, country_match = None, None, None

        for part in location_parts:
            city_row = cities_and_regions[cities_and_regions['city'].str.lower() == part]
            if not city_row.empty:
                city_match = city_row.iloc[0]['city']
                region_match = city_row.iloc[0]['region_en']
                country_match = city_row.iloc[0]['country']
                break
        
        # If no city match, check for region match
        if city_match is None:
            num_parts = len(location_parts)
            if num_parts > 3:
                # Join the middle parts for region match
                potential_region = ' '.join(location_parts[1:num_parts-1])
                region_row = cities_and_regions[(cities_and_regions['region_fi'].str.lower() == potential_region) | 
                                (cities_and_regions['region_en'].str.lower() == potential_region)]
                if not region_row.empty:
                    city_match = 'Unspecified'
                    region_match = region_row.iloc[0]['region_en']
                    country_match = region_row.iloc[0]['country']
                    
            elif num_parts == 3:
                # Join the middle parts for region match
                potential_region = ' '.join(location_parts[:num_parts-1])
                region_row = cities_and_regions[(cities_and_regions['region_fi'].str.lower() == potential_region) | 
                                (cities_and_regions['region_en'].str.lower() == potential_region) ]  
                if not region_row.empty:
                    city_match = 'Unspecified'
                    region_match = region_row.iloc[0]['region_en']
                    country_match = region_row.iloc[0]['country']
            else:
                for part in location_parts:
                    region_row = cities_and_regions[(cities_and_regions['region_fi'].str.lower() == part) | (cities_and_regions['region_en'].str.lower() == part)]
                    if not region_row.empty:
                        city_match = 'Unspecified'
                        region_match = region_row.iloc[0]['region_en']
                        country_match = region_row.iloc[0]['country']
                        break
        
        # If no city or region match, check for country
        if city_match is None and region_match is None:
            if 'finland' in location_parts:
                city_match = 'Unspecified'
                region_match = 'Unspecified'
                country_match = 'Finland'
            else:
                city_match = 'Unspecified'
                region_match = 'Unspecified'
                country_match = 'Unspecified'
        
        return city_match, region_match, country_match

    def normalize_location_text(self, text):
        if isinstance(text, str):
            text = text.replace('-', ' ')
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        return text


class SQLiteStorePipeline:

    def open_spider(self, spider):
        self.connection = sqlite3.connect("../../data/jobs.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute(
                """
                CREATE TABLE jobs(
                    date_posted TEXT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    city TEST,
                    region TEXT,
                    country TEXT,
                    seniorty_level TEXT,
                    employment_type TEXT,
                    job_function TEXT,
                    industries TEXT,
                    description TEXT,
                    job_url TEXT
                )
            """
            )
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        self.c.execute(
            """
            INSERT INTO jobs (date_posted,title,company,location,city,region,country,seniorty_level,employment_type,job_function,industries,description,job_url) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            (
                item["date_posted"],
                item["title"],
                item["company"],
                item["location"],
                item["city"],
                item["region"],
                item["country"],
                item["seniorty_level"],
                item["employment_type"],
                item["job_function"],
                item["industries"],
                item["description"],
                item["job_url"],
            ),
        )
        self.connection.commit()
        return item
