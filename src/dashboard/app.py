from load_data import *
from load_defaults import *
from pre_processing import *
from load_resources import *
from queries import *
from plots import *
from sidebar import *
import os

if __name__ == "__main__":
    app_path = os.path.dirname(os.path.abspath(__file__))
    app_path += '/../..'

    st.set_page_config(page_title="LinkedIn Job Analysis", layout="wide")

    st.markdown(
    """
    <style>
        .reportview-container {
            padding: 0;
        }
        .main {
            padding: 0;
        }
        .sidebar {
            padding: 0;
        }
    </style>
    <h1 style='text-align: center;'>LinkedIn Job Analysis Dashboard</h1>
    <p style='text-align: center;'>The data below updates daily and reflects the current job postings.</p>
    """,
    unsafe_allow_html=True
    )

    # For running locally
    # df = load_data_local(f"{app_path}/data/jobs.db")

    # For running on cloud
    df = load_data_cloud(f"{app_path}/data/jobs.db")

    countries = load_countries(app_path)
    default_country = "finland"
    default_country_index = (
        countries.index(default_country) if default_country in countries else 0
    )
    selected_country = sidebar_selectbox_country(countries, default_country_index)

    df = pre_processing(df, selected_country)

    regions = load_regions(app_path, selected_country)
    job_fields = load_job_fields(app_path, selected_country)
    seniority_levels = load_seniority_levels(app_path, selected_country)
    time_periods = load_time_periods(app_path, selected_country)

    default_region, default_job_field, default_seniority_level, default_time_period = (
        load_defaults(app_path, selected_country)
    )

    default_region_index = (
        regions.index(default_region) if default_region in regions else 0
    )
    default_job_field_index = (
        job_fields.index(default_job_field) if default_job_field in job_fields else 0
    )
    default_seniority_level_index = (
        seniority_levels.index(default_seniority_level)
        if default_seniority_level in seniority_levels
        else 0
    )
    default_time_period_index = (
        time_periods.index(default_time_period)
        if default_time_period in time_periods
        else 0
    )

    colors = ["#E57373", "#81C784", "#FFD54F", "#64B5F6", "#B39DDB", "#A1887F"]
    color_mapping = {level: color for level, color in zip(seniority_levels, colors)}
    color_sequence = [color_mapping[seniority] for seniority in seniority_levels]

    (
        selected_region,
        selected_job_field,
        selected_seniority_level,
        selected_time_period,
    ) = sidebar_selectbox_rest(
        regions,
        job_fields,
        seniority_levels,
        time_periods,
        default_region_index,
        default_job_field_index,
        default_seniority_level_index,
        default_time_period_index,
    )

    filtered_df = filter_jobs_by_selectbox(
        df,
        selected_region,
        selected_job_field,
        selected_seniority_level,
    )
    filtered_df = filter_by_time_period(filtered_df, selected_time_period)
    sidebar_put_result(filtered_df)

    job_counts = total_jobs_per_time_frequency(df, selected_time_period)
    
    count_seniority_levels = separate_for_seniority_levels(df, selected_region, selected_job_field, seniority_levels, selected_time_period)

    top_10_companies_selectbox = top_10_companies_by_selectbox(filtered_df)
    top_10_companies_field = top_10_companies_by_job_field_and_time_period(
        df, selected_job_field, selected_time_period
    )
    top_10_companies_region = top_10_companies_by_region_and_time_period(
        df, selected_region, selected_time_period
    )

    job_counts_by_field, sorted_job_fields = (
        total_jobs_by_region_and_time_period_across_job_fields_and_seniority_levels(
            df, selected_region, selected_time_period, seniority_levels
        )
    )
    job_counts_by_region, sorted_regions = (
        total_jobs_by_job_field_and_time_period_across_regions_and_seniority_levels(
            df, selected_job_field, selected_time_period, seniority_levels
        )
    )

    plot_line_total_jobs(job_counts, selected_time_period)

    col_pie_selectbox, col_bar_selectbox = st.columns([1, 2])
    with col_pie_selectbox, st.container(border=True):
        plot_pie_top_companies_seletbox(top_10_companies_selectbox, selected_region, selected_job_field, selected_seniority_level, selected_time_period)
    with col_bar_selectbox, st.container(border=True):
        plot_lines_total_jobs_selectbox_per_seniority_level(count_seniority_levels, selected_region, selected_job_field, seniority_levels, selected_time_period, color_mapping)

    col_pie_region, col_bar_region = st.columns([1, 2])
    with col_pie_region, st.container(border=True):
        plot_pie_top_companies_region(top_10_companies_region, selected_region, selected_time_period)
    with col_bar_region, st.container(border=True):
        plot_stacked_bar_chart_jobs_by_region_across_job_fields_and_seniority_levels_over_selected_time(
            job_counts_by_field,
            selected_region,
            color_sequence,
            sorted_job_fields,
            seniority_levels,
            selected_time_period
        )
    
    col_pie_job_field, col_bar_job_field = st.columns([1, 2])
    with col_pie_job_field, st.container(border=True):
        plot_pie_top_companies_field(top_10_companies_field, selected_job_field, selected_time_period)
    with col_bar_job_field, st.container(border=True):
        plot_stacked_bar_chart_jobs_by_job_field_across_regions_and_seniority_levels_over_selected_time(
            job_counts_by_region,
            selected_job_field,
            color_sequence,
            sorted_regions,
            seniority_levels,
            selected_time_period
        )
