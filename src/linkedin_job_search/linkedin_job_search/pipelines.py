import datetime
import json
import logging
import os
import unicodedata

import pandas as pd
import psycopg2
from bs4 import BeautifulSoup
from dotenv import dotenv_values


class LinkedinJobSearchPipeline:
    def __init__(self, country_name):
        config_file_cities_and_regions = os.path.join(
            os.getcwd(),
            f"../../resources/{country_name.lower()}/cities_and_regions_{country_name.lower()}.json",
        )
        self.cities_and_regions = pd.read_json(config_file_cities_and_regions)

        config_file_job_fields = os.path.join(
            os.getcwd(),
            f"../../resources/{country_name.lower()}/job_fields_{country_name.lower()}.json",
        )
        with open(config_file_job_fields) as file:
            job_fields = json.load(file)
        self.alternative_to_field = {}
        for field in job_fields:
            for alt in field["alternatives"]:
                self.alternative_to_field[alt.lower()] = field["name"]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(country_name=crawler.spider.country_name)

    def process_item(self, item, spider):
        item["title"] = (
            item["title"].strip().replace("\n", "").replace(",", "").strip()
            if item["title"]
            else "Unspecified"
        )
        item["company"] = (
            item["company"].strip().replace("\n", "").replace(",", "").strip()
            if item["company"]
            else "Unspecified"
        )
        item["location"] = (
            item["location"].strip().replace("\n", "").replace(",", "").strip()
            if item["location"]
            else "Unspecified"
        )
        item["city"], item["region"], item["country"] = self.normalize_location(
            item["location"]
        )
        item["date_posted"] = (
            item["date_posted"].strip().replace("\n", "").replace(",", "").strip()
            if item["date_posted"]
            else "Unspecified"
        )
        item["date_posted"] = self.normalize_date(item["date_posted"])
        item["seniority_level"] = (
            item["seniority_level"].strip().replace("\n", "").replace(",", "").strip()
            if item["seniority_level"]
            else ""
        )
        item["employment_type"] = (
            item["employment_type"].strip().replace("\n", "").replace(",", "").strip()
            if item["employment_type"]
            else "Unspecified"
        )
        item["job_function"] = (
            item["job_function"].strip().replace("\n", "").replace(",", "").strip()
            if item["job_function"]
            else "Unspecified"
        )
        item["job_fields"] = self.normalize_job_function(item["job_function"])
        item["industries"] = (
            item["industries"].strip().replace("\n", "").replace(",", "").strip()
            if item["industries"]
            else "Unspecified"
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

    def normalize_location(self, location):
        location = self.normalize_location_text(location)
        location = location.lower()
        location = location.replace("sub region", "")
        location = location.replace("northen", "north")
        location = location.replace("southern", "south")
        location = location.replace("savonia", "savo")
        location_parts = location.split()
        city_match, region_match, country_match = None, None, None

        for part in location_parts:
            city_row = self.cities_and_regions[
                self.cities_and_regions["city"].str.lower() == part
            ]
            if not city_row.empty:
                city_match = city_row.iloc[0]["city"]
                region_match = city_row.iloc[0]["region_en"]
                country_match = city_row.iloc[0]["country"]
                break

        # If no city match, check for region match
        if city_match is None:
            num_parts = len(location_parts)
            if num_parts > 3:
                # Join the middle parts for region match
                potential_region = " ".join(location_parts[1 : num_parts - 1])
                region_row = self.cities_and_regions[
                    (
                        self.cities_and_regions["region_fi"].str.lower()
                        == potential_region
                    )
                    | (
                        self.cities_and_regions["region_en"].str.lower()
                        == potential_region
                    )
                ]
                if not region_row.empty:
                    city_match = "Unspecified"
                    region_match = region_row.iloc[0]["region_en"]
                    country_match = region_row.iloc[0]["country"]

            elif num_parts == 3:
                # Join the middle parts for region match
                potential_region = " ".join(location_parts[: num_parts - 1])
                region_row = self.cities_and_regions[
                    (
                        self.cities_and_regions["region_fi"].str.lower()
                        == potential_region
                    )
                    | (
                        self.cities_and_regions["region_en"].str.lower()
                        == potential_region
                    )
                ]
                if not region_row.empty:
                    city_match = "Unspecified"
                    region_match = region_row.iloc[0]["region_en"]
                    country_match = region_row.iloc[0]["country"]
            else:
                for part in location_parts:
                    region_row = self.cities_and_regions[
                        (self.cities_and_regions["region_fi"].str.lower() == part)
                        | (self.cities_and_regions["region_en"].str.lower() == part)
                    ]
                    if not region_row.empty:
                        city_match = "Unspecified"
                        region_match = region_row.iloc[0]["region_en"]
                        country_match = region_row.iloc[0]["country"]
                        break

        # If no city or region match, check for country
        if city_match is None and region_match is None:
            if "finland" in location_parts:
                city_match = "Unspecified"
                region_match = "Unspecified"
                country_match = "Finland"
            else:
                city_match = "Unspecified"
                region_match = "Unspecified"
                country_match = "Unspecified"

        return city_match, region_match, country_match

    def normalize_location_text(self, text):
        if isinstance(text, str):
            text = text.replace("-", " ")
            text = (
                unicodedata.normalize("NFKD", text)
                .encode("ASCII", "ignore")
                .decode("utf-8")
            )
        return text

    def normalize_job_function(self, job_function):
        job_function_lower = job_function.lower()
        matched_fields = []

        if job_function_lower in self.alternative_to_field:
            matched_fields.append(self.alternative_to_field[job_function_lower])
        else:
            for alt, field_name in self.alternative_to_field.items():
                if alt in job_function_lower and field_name not in matched_fields:
                    matched_fields.append(field_name)

        return json.dumps(matched_fields if matched_fields else ["Other"])


class PostgresPipeline:
    def __init__(self):
        secrets = dotenv_values(os.path.join(os.getcwd(), "../../configs/.env"))
        self.user = secrets["POSTGRES_USER"]
        self.password = secrets["POSTGRES_PASSWORD"]
        self.host = secrets["POSTGRES_HOST"]
        self.port = secrets["POSTGRES_PORT"]
        self.dbname = secrets["POSTGRES_DBNAME"]

    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cursor = self.conn.cursor()
            logging.log(logging.DEBUG, "Successfully connected to PostgreSQL")

            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    date_posted TEXT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    city TEST,
                    region TEXT,
                    country TEXT,
                    seniority_level TEXT,
                    employment_type TEXT,
                    job_function TEXT,
                    job_fields TEXT,
                    industries TEXT,
                    description TEXT,
                    job_url TEXT
                );
            """
            )
            
            self.conn.commit()
        except psycopg2.Error as e:
            logging.log(logging.ERROR, f"Failed to connect to PostgreSQL: {e}")
            raise e

    def close_spider(self, spider):
        if self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            logging.log(logging.DEBUG, "Closed PostgreSQL connection")

    def process_item(self, item, spider):
        try:
            # Check if job_url already exists for today (same date)
            date_part = item["date_posted"].split()[0] if item["date_posted"] else None
            
            self.cursor.execute(
                "SELECT 1 FROM jobs WHERE job_url = %s AND date_posted LIKE %s LIMIT 1",
                (item["job_url"], f"{date_part}%")
            )
            
            if self.cursor.fetchone():
                # Job already exists for today, skip insertion
                logging.log(
                    logging.DEBUG,
                    f"Duplicate job skipped (same URL on {date_part}): {item['job_url']}"
                )
                return item
            
            # Insert new job
            self.cursor.execute(
                """
                INSERT INTO jobs (date_posted,title,company,location,city,region,country,seniority_level,employment_type,job_function,job_fields,industries,description,job_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    item["date_posted"],
                    item["title"],
                    item["company"],
                    item["location"],
                    item["city"],
                    item["region"],
                    item["country"],
                    item["seniority_level"],
                    item["employment_type"],
                    item["job_function"],
                    item["job_fields"],
                    item["industries"],
                    item["description"],
                    item["job_url"],
                ),
            )

            self.conn.commit()

        except psycopg2.Error as e:
            logging.error(f"Error inserting data: {e}")
        return item
