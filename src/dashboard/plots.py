import streamlit as st
import plotly.express as px


def plot_line_total_jobs_selectbox(job_counts_selectbox, selected_region, selected_job_field, selected_seniority_level, selected_time_period):
    text_helper = ''
    if selected_time_period == 'Any time':
        text_helper = 'for all the time'
    elif selected_time_period == 'day':
        text_helper = 'on a daily basis'
    else:
        text_helper = f'on a {selected_time_period}ly basis'
    fig_total_jobs_per_month_selectbox = px.line(
        job_counts_selectbox,
        x=selected_time_period,
        y="job_count",
        title=f"Number of jobs posted for {selected_job_field} in {selected_region} <br> for {selected_seniority_level} {text_helper}",
        labels={"range": selected_time_period, "job_count": "Number of Jobs"},
    )
    fig_total_jobs_per_month_selectbox.update_traces(line=dict(color="#008080"))
    fig_total_jobs_per_month_selectbox.update_layout(
        title=dict(
            xanchor='center',  
            x=0.5,
        )
    )
    st.plotly_chart(fig_total_jobs_per_month_selectbox)


def plot_pie_top_companies_seletbox(top_15_companies_selectbox, selected_region, selected_job_field, selected_seniority_level, selected_time_period):
    pie_top_companies_selectbox = px.pie(
        top_15_companies_selectbox,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_selectbox.update_traces(
    textinfo='percent', 
    textposition='inside',    
    )
    pie_top_companies_selectbox.update_layout(
        autosize=False,
        legend=dict(
            orientation='h',            
            yanchor='top',
            y=0.0,                    
            xanchor='left',
            x=0.0,
            itemwidth=50      
        ),
        title=dict(
            xanchor='center',  
            x=0.5,
            subtitle=dict(
                text=f'for {selected_job_field} <br> in {selected_region} for {selected_seniority_level} for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}'
            )
        ),
        margin=dict(l=0, r=0),
    ) 
    st.plotly_chart(pie_top_companies_selectbox)


def plot_pie_top_companies_field(top_15_companies_field, selected_job_field, selected_time_period):
    pie_top_companies_field = px.pie(
        top_15_companies_field,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_field.update_traces(
    textinfo='percent', 
    textposition='inside',    
    )
    pie_top_companies_field.update_layout(
        autosize=False,
        legend=dict(
            orientation='h',        
            yanchor='top',
            y=0.0,                 
            xanchor='left',
            x=0.0,
            itemwidth=50              
        ),
        title=dict(
            xanchor='center',  
            x=0.5,
            subtitle=dict(
                text=f'for {selected_job_field} <br> in all regions for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}'
            )
        ),
        margin=dict(l=0, r=0),
    ) 
    st.plotly_chart(pie_top_companies_field, use_container_width=True)


def plot_pie_top_companies_region(top_15_companies_region, selected_region, selected_time_period):
    pie_top_companies_region = px.pie(
        top_15_companies_region,
        names="company",
        values="job_count",
        title=f"10 most recruiting companies",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    pie_top_companies_region.update_traces(
    textinfo='percent', 
    textposition='inside',     
    )
    pie_top_companies_region.update_layout(
        autosize=False,
        legend=dict(
            orientation='h',           
            yanchor='top',
            y=0.0,                  
            xanchor='left',
            x=0.0,
            itemwidth=50             
        ),
        title=dict(
            xanchor='center',  
            x=0.5,
            subtitle=dict(
                text=f'in {selected_region} <br>  for all job fields for {selected_time_period.lower() if selected_time_period == 'Any time' else 'the past '+selected_time_period}'
            )
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
    selected_time_period
):
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
            xanchor='center',  
            x=0.5,  
        )
    )
    st.plotly_chart(fig_region_jobs)


def plot_stacked_bar_chart_jobs_by_job_field_across_regions_and_seniority_levels_over_selected_time(
    job_counts_by_region,
    selected_job_field,
    color_sequence,
    sorted_regions,
    seniority_levels,
    selected_time_period
):
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
            xanchor='center',  
            x=0.5,  
        )
    )
    st.plotly_chart(fig_field_jobs)

