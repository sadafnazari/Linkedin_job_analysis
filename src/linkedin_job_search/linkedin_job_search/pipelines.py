import sqlite3
import datetime
from bs4 import BeautifulSoup


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


class SQLiteStorePipeline:

    def open_spider(self, spider):
        self.connection = sqlite3.connect("jobs.db")
        self.c = self.connection.cursor()
        try:
            self.c.execute(
                """
                CREATE TABLE jobs(
                    date_posted TEXT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
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
            INSERT INTO jobs (date_posted,title,company,location,seniorty_level,employment_type,job_function,industries,description,job_url) VALUES(?,?,?,?,?,?,?,?,?,?)
        """,
            (
                item["date_posted"],
                item["title"],
                item["company"],
                item["location"],
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
