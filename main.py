import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="TB Burden Dashboard", layout="wide")
st.title("🌍 Tuberculosis (TB) Burden Dashboard")
st.markdown("""
This interactive dashboard visualizes **estimated TB prevalence** across countries and years.
You can explore trends, uncertainty intervals, and compare prevalence between nations. Please select filters from 
the sidebar to customize the visualizations.
""")

@st.cache_data
def clean_data():
    df = pd.read_csv('TB_Burden_Country.csv')
    df = df.drop(['ISO 2-character country/territory code','ISO numeric country/territory code',
                      'ISO 3-character country/territory code', 'Region','Method to derive TBHIV estimates'], axis=1)
    df = df.rename(columns={'Country or territory name':'country',
                                'Estimated prevalence of TB (all forms)':'estimated_prevalence',
                                'Estimated prevalence of TB (all forms), low bound':'estimated_prevalence_low',
                                'Estimated prevalence of TB (all forms), high bound':'estimated_prevalence_high',
                                'Year':'year'})
    return df

data = clean_data()

def plot_tb_prevalence(df, country):
    df_country = df[df['country'] == country]

    fig = px.bar(
        df_country,
        x='year',
        y='estimated_prevalence',
        error_y='estimated_prevalence_high',
        error_y_minus='estimated_prevalence_low',
        title=f'TB Prevalence in {country} (with uncertainty)',
        color_discrete_sequence=['steelblue']
    )

    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Estimated Prevalence of TB (all forms)',
        template='plotly_white',
        hovermode='x unified',
        height=500,
        width=800
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_compare_countries(df, countries, year_sel):
    years = [year_sel[0], year_sel[-1]]

    dfs = {
        year: df[
            (df['year'] == year) &
            (df['country'].isin(countries))
        ].sort_values('country')
        for year in years
    }

    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        subplot_titles=[f"{years[0]}", f"{years[1]}"]
    )

    for i, year in enumerate(years):
        data = dfs[year]
        if data.empty:
            continue  # skip if no data for selected countries

        y = data['country']
        x = data['estimated_prevalence']
        error_minus = data['estimated_prevalence_low']
        error_plus = data['estimated_prevalence_high']

        fig.add_trace(
            go.Bar(
                x=x,
                y=y,
                orientation='h',
                error_x=dict(
                    type='data',
                    symmetric=False,
                    array=error_plus - x,
                    arrayminus=x - error_minus,
                    color='rgba(100,100,100,0.6)'
                ),
                name=str(year),
                hovertemplate=(
                    f"<b>%{{y}}</b><br>"
                    f"Year: {year}<br>"
                    "Prevalence: %{x}<br>"
                    "<extra></extra>"
                ),
                marker_color='skyblue' if i == 0 else 'lightgreen'
            ),
            row=1, col=i+1
        )

    fig.update_xaxes(
        type='log',
        title_text="Estimated TB Prevalence (log scale)"
    )
    fig.update_yaxes(title_text="Country", automargin=True)

    fig.update_layout(
        title_text=f"Comparison of TB Prevalence ({years[0]} vs {years[1]})",
        height=600,
        width=1200,
        showlegend=False,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

st.sidebar.header("Filters")
select_plot = st.sidebar.selectbox(
    "Which plot do you want to see?",
    ("TB Prevalence Over Time", "Compare Countries with Time")
)
if select_plot == "Compare Countries with Time":
    countries = st.sidebar.multiselect(
        "Select Countries to Compare",
        options=data['country'].unique()
    )
    year_sel = st.sidebar.slider(
        "Select Years to compare",
        min_value=int(data['year'].min()),
        max_value=int(data['year'].max()),
        value=(int(data['year'].min()), int(data['year'].max()))
    )
    plot_compare_countries(data, countries, year_sel)
else:
    country = st.sidebar.selectbox(
        "Select Country",
        options=data['country'].unique()
    )
    plot_tb_prevalence(data, country)