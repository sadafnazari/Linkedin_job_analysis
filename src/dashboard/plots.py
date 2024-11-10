import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


def plot_line_total_jobs(job_counts, selected_time_period):
    """
    Plots a line chart showing the total number of jobs posted over a specified time period.

    Parameters:
    job_counts (pandas.DataFrame): A DataFrame containing job count data with columns for
                                   the time period and job count. The DataFrame should have at least
                                   two columns: one for the time period and another for job counts.
    selected_time_period (str): The time period to group the job counts by (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the line chart using Streamlit's plotly_chart function.
    """
    text_helper = ""
    if selected_time_period == "Any time":
        text_helper = "for all the time"
    elif selected_time_period == "day":
        text_helper = "on a daily basis"
    else:
        text_helper = f"on a {selected_time_period}ly basis"
    fig_total_jobs = px.line(
        job_counts,
        x=selected_time_period,
        y="job_count",
        title=f"Number of jobs posted {text_helper}",
        labels={"range": selected_time_period, "job_count": "Number of Jobs"},
    )
    fig_total_jobs.update_traces(line=dict(color="#008080"))
    fig_total_jobs.update_layout(
        title=dict(
            xanchor="center",
            x=0.5,
        )
    )
    st.plotly_chart(fig_total_jobs)


def plot_lines_total_jobs_selectbox_per_seniority_level(
    count_seniority_levels,
    selected_region,
    selected_job_field,
    seniority_levels,
    selected_time_period,
    color_mapping,
):
    """
    Plots a line chart showing the total number of jobs posted across different seniority levels.

    This function generates a line chart for each seniority level, displaying the number of jobs posted 
    over a selected time period for a specified region and job field.

    Parameters:
    count_seniority_levels (list of pandas.DataFrame): A list of DataFrames, where each DataFrame contains 
                                                       job count data for a specific seniority level. Each DataFrame 
                                                       must include columns for the time period and job counts.
    selected_region (str): The region for which job data is displayed.
    selected_job_field (str): The job field for which job data is displayed.
    seniority_levels (list of str): A list of seniority levels to display on the chart.
    selected_time_period (str): The time period to group the job counts by (e.g., "Any time", "day", "month").
    color_mapping (dict): A dictionary mapping each seniority level to a color for the chart lines.

    Returns:
    None: This function does not return a value. It directly renders the line chart using Streamlit's plotly_chart function.
    """
    text_helper = ""
    if selected_time_period == "Any time":
        text_helper = "for all the time"
    elif selected_time_period == "day":
        text_helper = "on a daily basis"
    else:
        text_helper = f"on a {selected_time_period}ly basis"
    fig_total_jobs_selectbox_per_seniority_level = go.Figure()
    for level, df_level in zip(seniority_levels, count_seniority_levels):
        fig_total_jobs_selectbox_per_seniority_level.add_trace(
            go.Scatter(
                x=df_level[selected_time_period],
                y=df_level["job_count"],
                mode="lines",
                name=level,
                line=dict(color=color_mapping[level]),
            )
        )
    fig_total_jobs_selectbox_per_seniority_level.update_layout(
        title=f"Number of jobs posted for {selected_job_field} in {selected_region} <br> for seniority_levels {text_helper}",
        xaxis_title="Date",
        yaxis_title="Number of Jobs",
        legend_title="Seniority Level",
        template="plotly_white",
    )
    fig_total_jobs_selectbox_per_seniority_level.update_layout(
        title=dict(
            xanchor="center",
            x=0.5,
        )
    )
    st.plotly_chart(fig_total_jobs_selectbox_per_seniority_level)


def plot_pie_top_companies_seletbox(
    top_10_companies_selectbox,
    selected_region,
    selected_job_field,
    selected_seniority_level,
    selected_time_period,
):
    """
    Plots a pie chart showing the top 10 companies with the highest number of job postings.

    This function generates a pie chart that displays the distribution of job postings across the top 10 companies.

    Parameters:
    top_10_companies_selectbox (pandas.DataFrame): A DataFrame containing the job count data for the top 10 companies.
                                                  It must include columns for the company name ('company') and the 
                                                  number of job postings ('job_count').
    selected_region (str): The region for which the job data is displayed.
    selected_job_field (str): The job field for which job data is displayed.
    selected_seniority_level (str): The selected seniority level.
    selected_time_period (str): The selected time period to filter the job postings (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the pie chart using Streamlit's plotly_chart function.
    """
    pie_top_companies_selectbox = px.pie(
        top_10_companies_selectbox,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_selectbox.update_traces(
        textinfo="percent",
        textposition="inside",
    )
    pie_top_companies_selectbox.update_layout(
        autosize=False,
        legend=dict(
            orientation="h", yanchor="top", y=0.0, xanchor="left", x=0.0, itemwidth=50
        ),
        title=dict(
            xanchor="center",
            x=0.5,
            subtitle=dict(
                text=f"for {selected_job_field} <br> in {selected_region} for {selected_seniority_level} for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}"
            ),
        ),
        margin=dict(l=0, r=0),
    )
    st.plotly_chart(pie_top_companies_selectbox)


def plot_pie_top_companies_field(
    top_10_companies_field, selected_job_field, selected_time_period
):
    """
    Plots a pie chart showing the top 05 companies with the highest number of job postings
    for a specific job field and time period.

    This function generates a pie chart displaying the distribution of job postings across 
    the top 10 companies for the selected job field and time period.

    Parameters:
    top_10_companies_field (pandas.DataFrame): A DataFrame containing the job count data 
                                                for the top 10 companies in the selected 
                                                job field. It must include columns for 
                                                the company name ('company') and the 
                                                number of job postings ('job_count').
    selected_job_field (str): The job field for which job data is displayed (e.g., "Software Engineering").
    selected_time_period (str): The selected time period to filter the job postings (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the pie chart using Streamlit's plotly_chart function.
    """
    pie_top_companies_field = px.pie(
        top_10_companies_field,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_field.update_traces(
        textinfo="percent",
        textposition="inside",
    )
    pie_top_companies_field.update_layout(
        autosize=False,
        legend=dict(
            orientation="h", yanchor="top", y=0.0, xanchor="left", x=0.0, itemwidth=50
        ),
        title=dict(
            xanchor="center",
            x=0.5,
            subtitle=dict(
                text=f"for {selected_job_field} <br> in all regions for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}"
            ),
        ),
        margin=dict(l=0, r=0),
    )
    st.plotly_chart(pie_top_companies_field, use_container_width=True)


def plot_pie_top_companies_region(
    top_10_companies_region, selected_region, selected_time_period
):
    """
    Plots a pie chart showing the top 10 companies with the highest number of job postings
    in a selected region, across all job fields, for a specific time period.

    This function generates a pie chart displaying the distribution of job postings across 
    the top 10 companies in the selected region and time period.

    Parameters:
    top_10_companies_region (pandas.DataFrame): A DataFrame containing the job count data 
                                                for the top 10 companies in the selected 
                                                region. It must include columns for 
                                                the company name ('company') and the 
                                                number of job postings ('job_count').
    selected_region (str): The region for which job data is displayed.
    selected_time_period (str): The selected time period to filter the job postings (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the pie chart using Streamlit's plotly_chart function.
    """
    pie_top_companies_region = px.pie(
        top_10_companies_region,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_region.update_traces(
        textinfo="percent",
        textposition="inside",
    )
    pie_top_companies_region.update_layout(
        autosize=False,
        legend=dict(
            orientation="h", yanchor="top", y=0.0, xanchor="left", x=0.0, itemwidth=50
        ),
        title=dict(
            xanchor="center",
            x=0.5,
            subtitle=dict(
                text=f"in {selected_region} <br>  for all job fields for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}"
            ),
        ),
        margin=dict(l=0, r=0),
    )
    st.plotly_chart(pie_top_companies_region, use_container_width=True)


def plot_stacked_bar_chart_jobs_by_region_across_job_fields_and_seniority_levels_over_selected_time(
    job_counts_by_field,
    selected_region,
    color_sequence,
    sorted_job_fields,
    seniority_levels,
    selected_time_period,
):
    """
    Plots a stacked bar chart showing the number of jobs in a selected region, across 
    all job fields and seniority levels, for a given time period.

    This function creates a stacked bar chart where each bar represents the total number 
    of jobs in a job field for a specific region, broken down by seniority level.

    Parameters:
    job_counts_by_field (pandas.DataFrame): A DataFrame containing job count data 
                                              for each job field, including columns 
                                              for 'job_fields', 'count', and 'seniority_level'.
    selected_region (str): The region for which the job data is displayed.
    color_sequence (list): A list of color values for differentiating seniority levels in the stacked bars.
    sorted_job_fields (list): A sorted list of job fields used to order the bars on the x-axis.
    seniority_levels (list): A list of seniority levels used for grouping the data in the chart.
    selected_time_period (str): The selected time period for filtering the job postings 
                                (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the stacked bar chart 
          using Streamlit's plotly_chart function.
    """
    fig_region_jobs = px.bar(
        job_counts_by_field,
        x="job_fields",
        y="count",
        color="seniority_level",
        color_discrete_sequence=color_sequence,
        title=f"Number of jobs in {selected_region} <br> across all job fields and seniority levels <br> for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}",
        labels={
            "job_fields": "Job Field",
            "count": "Number of Jobs",
            "seniority_level": "Seniority Level",
        },
        category_orders={
            "job_fields": sorted_job_fields,
            "seniority_level": seniority_levels,
        },
        barmode="stack",
    )
    fig_region_jobs.update_layout(
        xaxis_tickangle=90,
        title=dict(
            xanchor="center",
            x=0.5,
        ),
    )
    st.plotly_chart(fig_region_jobs)


def plot_stacked_bar_chart_jobs_by_job_field_across_regions_and_seniority_levels_over_selected_time(
    job_counts_by_region,
    selected_job_field,
    color_sequence,
    sorted_regions,
    seniority_levels,
    selected_time_period,
):
    """
    Plots a stacked bar chart showing the number of jobs for a selected job field, 
    across all regions and seniority levels, for a given time period.

    This function creates a stacked bar chart where each bar represents the total 
    number of jobs in a region for a specific job field, broken down by seniority level.

    Parameters:
    job_counts_by_region (pandas.DataFrame): A DataFrame containing job count data 
                                              for each region, including columns 
                                              for 'region', 'count', and 'seniority_level'.
    selected_job_field (str): The job field for which the job data is displayed.
    color_sequence (list): A list of color values for differentiating seniority levels 
                           in the stacked bars.
    sorted_regions (list): A sorted list of regions used to order the bars on the x-axis.
    seniority_levels (list): A list of seniority levels for grouping the data in the chart.
    selected_time_period (str): The selected time period for filtering the job postings 
                                (e.g., "Any time", "day", "month").

    Returns:
    None: This function does not return a value. It directly renders the stacked bar chart 
          using Streamlit's plotly_chart function.
    """
    fig_field_jobs = px.bar(
        job_counts_by_region,
        x="region",
        y="count",
        color="seniority_level",
        color_discrete_sequence=color_sequence,
        title=f"Number of jobs for {selected_job_field} <br> across all regions and seniority levels <br> for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}",
        labels={
            "region": "Region",
            "count": "Number of Jobs",
            "seniority_level": "Seniority Level",
        },
        category_orders={"region": sorted_regions, "seniority_level": seniority_levels},
        barmode="stack",
    )
    fig_field_jobs.update_layout(
        xaxis_tickangle=90,
        title=dict(
            xanchor="center",
            x=0.5,
        ),
    )
    st.plotly_chart(fig_field_jobs)
