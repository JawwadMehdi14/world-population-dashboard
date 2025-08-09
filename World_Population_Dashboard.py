import numpy as np
import pandas as pd
import seaborn as sns
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import plotly.express as px
import missingno as msno
import plotly.offline as py
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

py.init_notebook_mode(connected=True)

import warnings
warnings.filterwarnings('ignore')

# Load the World Population dataset
df = pd.read_csv('C:/Users/User/Downloads/countries-table.csv')

# Define the Dash app
app = dash.Dash(__name__)

# Get the unique years from the dataset
years = ['1980', '2000', '2010', '2022', '2023', '2030', '2050']

# Create the options for the dropdown
dropdown_options = [{'label': year, 'value': year} for year in years]

# Create the options for the country dropdown
country_dropdown_options = [{'label': country, 'value': country} for country in df['country'].unique()]

# Define the app layout
app.layout = html.Div(
    children=[
        html.H1("World Population Analysis", style={'text-align': 'center', 'font-size': '48px', 'color': 'darkblue', 'margin-bottom': '20px'}),
        html.Div(
            children=[
                html.Label("Select Year:", style={'font-weight': 'bold'}),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=dropdown_options,
                    value='2023',  # Set the initial value to '2023'
                    style={'width': '200px', 'margin-left': '10px'}
                ),
            ],
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-bottom': '30px'}
        ),
        dcc.Graph(id="choropleth-graph"),
        html.H2("Top 10 Countries with the Most Population", style={'text-align': 'center', 'font-size': '36px', 'color': 'darkblue', 'margin-top': '40px'}),
        dcc.Graph(id="bar-graph"),
        html.H2("Pie Chart - Share of Area by Country", style={'text-align': 'center', 'font-size': '36px', 'color': 'darkblue', 'margin-top': '40px'}),
        dcc.Graph(id="pie-chart"),
        html.Div(
            children=[
                html.Label("Select Country:", style={'font-weight': 'bold'}),
                dcc.Dropdown(
                    id="country-dropdown",
                    options=country_dropdown_options,
                    value=df['country'].iloc[0],  # Set the initial value to the first country in the dataset
                    style={'width': '200px', 'margin-left': '10px'}
                ),
            ],
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-bottom': '30px'}
        ),
        html.H2("Line Chart - Population Growth", style={'text-align': 'center', 'font-size': '36px', 'color': 'darkblue', 'margin-top': '40px'}),
        dcc.Graph(id="line-chart"),
        html.H2("Bar Graph - Population Distribution", style={'text-align': 'center', 'font-size': '36px', 'color': 'darkblue', 'margin-top': '40px'}),
        dcc.Graph(id="histogram"),
    ],
    style={'padding': '50px'}
)


# Define the callback function for the choropleth graph
@app.callback(
    Output("choropleth-graph", "figure"),
    Input("year-dropdown", "value")
)
def update_choropleth_graph(selected_year):
    # Create the choropleth graph for the selected year
    fig = px.choropleth(
        df,
        locations='country',
        locationmode='country names',
        color=f'pop{selected_year}',  # We indicate the year we are interested in
        hover_name='country',
        title=f'{selected_year} Population',
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    # Get the top 10 countries with the most population for the selected year
    top_countries = df[['country', f'pop{selected_year}']].nlargest(10, f'pop{selected_year}')
    
    # Add annotations for the top 10 countries
    for index, row in top_countries.iterrows():
        fig.add_annotation(
            x=row['country'],
            y=row[f'pop{selected_year}'],
            text=str(row[f'pop{selected_year}']),
            showarrow=True,
            arrowhead=1,
            font=dict(color='black', size=10),
            ax=0,
            ay=-40
        )

    return fig


# Define the callback function for the bar graph
@app.callback(
    Output("bar-graph", "figure"),
    Input("year-dropdown", "value")
)
def update_bar_graph(selected_year):
    # Get the top 10 countries with the most population for the selected year
    top_countries = df[['country', f'pop{selected_year}']].nlargest(10, f'pop{selected_year}')

    # Create the bar graph
    fig = px.bar(
        top_countries,
        x='country',
        y=f'pop{selected_year}',
        color=f'pop{selected_year}',
        title=f'Top 10 Countries with the Most Population - {selected_year}'
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    return fig



# Update the callback function for the pie chart
@app.callback(
    Output("pie-chart", "figure"),
    Input("year-dropdown", "value")
)
def update_pie_chart(selected_year):
    # Calculate the share of area for each country
    df['area_share'] = df['area'] / df['area'].sum()

    # Create the pie chart
    fig = px.pie(
        df,
        values='area_share',
        names='country',
        title='Share of Area by Country',
        hover_data=['area'],
        labels={'area_share': 'Area Share', 'country': 'Country'}
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Increase the size of the pie chart by ten times
    fig.update_layout(height=1000, width=1000)

    return fig



# Define the callback function for the line chart
@app.callback(
    Output("line-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_line_chart(selected_country):
    # Get the population data for the selected country
    country_data = df.loc[df['country'] == selected_country, 'pop1980':'pop2050']

    # Create the line chart
    fig = px.line(
        country_data.T,
        x=country_data.columns,
        y=country_data.values[0],
        title=f'Population Growth - {selected_country}',
        labels={'x': 'Year', 'y': 'Population'}
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    return fig


# Update the callback function for the histogram
@app.callback(
    Output("histogram", "figure"),
    Input("country-dropdown", "value")
)
def update_histogram(selected_country):
    # Get the population data for the selected country
    country_data = df.loc[df['country'] == selected_country, ['pop1980', 'pop2000', 'pop2010', 'pop2022', 'pop2023', 'pop2030', 'pop2050']]

    # Reshape the data for the histogram
    data = country_data.values.flatten()

    # Create the histogram
    fig = px.histogram(
        x=years,
        y=data,
        title=f'Population Distribution - {selected_country}',
        labels={'x': 'Year', 'y': 'Population'}
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=80, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )

    return fig






# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
