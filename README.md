# LinkedIn job analysis

LinkedIn Job Analysis project is based on the jobs, that are publicly available on Linkedin and the scraped data will remain under LinkedIn ownership.

The analytics dashboard is deployed on the <a href="https://linkedin-job-analysis-dashboard.streamlit.app/">Streamlit Community Cloud</a>.

This project has two parts:
- Scraping: <a href="src/linkedin_job_search/README.md">linkedin_job_search</a> is the part of the project, responsible for scraping Linkedin job posts.
- Analytics dashboard: <a href="src/dashboard/README.md">dashboard</a> is the part of project, responsible for analytics dashboard.


## Notes

- This project is only implemented for learning purposes, and any inappropriate use of data is not the author's responsibility.

- While the project is defined to be as generalized as possible, the current functionalities have been tested on Finland job market.

- LinkedIn enforces a 1000-result limit per search query. For comprehensive data collection, use overlapping time windows to ensure complete coverage.

## References

The `cities_and_regions_finland.json` file has been a modified version of the available list of cities and regions from <a href='https://simplemaps.com/data/fi-cities'>simplemaps</a> website.
