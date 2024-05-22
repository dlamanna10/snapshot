import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import base64
import io
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pycountry_convert import country_alpha2_to_country_name

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # Snapshot Header
    html.Div([
        html.Div([
            html.H1('Snapshot: Data Visualization', className='header'),
            html.Div([
                html.H1("Upload:", className='upload-heading'),
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files', className='font-weight-bold')
                    ]),
                    className='upload',
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
            ], className='upload-container')
        ], className='header-container')
    ]),
    
    # Instructions Box
    dbc.Card(
        dbc.CardBody([
            html.H3("Instructions", className='instructions-heading'),
            html.P("To get started, convert your DistroKid tsv file to a csv file and upload it above. Then, scroll to the graph that you want to utilize and begin!", className='instructions-text')
        ]),
        className="m-0 instructions-container",
    ),
    
    # Main Content
    html.Div([
        html.Div([
            html.H2("Earnings per Stream", className='graph-heading'),
            dcc.Graph(id='graph-earnings-per-stream', className='graph'),
        ], className='col-md-8 graph-container'),  # Graph on the left with graph-container class
        html.Div([
            html.H2("Parameters", className='graph-heading'),
            html.Div([
                html.Label("Select Songs:", className='dropdown-label'),
                dcc.Dropdown(id='dropdown-song', multi=True, className='dropdown')
            ], className='dropdown-container'),  # Add dropdown-container class
            html.Div([
                html.Label("Select Store:", className='dropdown-label'),
                dcc.Dropdown(id='dropdown-store', className='dropdown', multi=False)
            ], className='dropdown-container'),  # Add dropdown-container class
            html.Div(id='graph-description', className='graph-description')  # Div for graph description
        ], className='col-md-4 graph-container'),  # Dropdown menus on the right with dropdown-container class
    ], className='row', style={'margin-left': '10px', 'margin-right': '10px'}),  # Use Bootstrap grid system to align side by side

    html.Div([
        html.Div([
            html.H3("Total Streams by Country (Excluding US)", className='graph-heading'),
            dcc.Graph(id='total-streams-by-country-1', className='graph'),  # Use a container div for multiple graphs
        ], className='col-md-6 graph-container'),  # Half-width container for the new graph
        html.Div([
            html.H3("Total Streams by Country", className='graph-heading'),
            dcc.Graph(id='total-streams-by-country-2', className='graph'),  # Use a container div for multiple graphs
        ], className='col-md-6 graph-container'),  # Half-width container for the new graph
    ], className='row', style={'margin-left': '10px', 'margin-right': '10px'}),  # Use Bootstrap grid system

    # New Section for Total Streams and Earnings Chart
    html.Div([
    html.H2("Total Streams", className='graph-heading'),
    dcc.Graph(id='total-streams-chart', className='graph'),
    html.Div([
        # Dropdowns and Date Picker in one row
        html.Div([
            html.Label("Select Songs:", className='dropdown-label'),
            dcc.Dropdown(id='dropdown-total-song-streams', multi=True, className='dropdown', style={'width': '100%', 'display': 'inline-block'})
        ], className='dropdownchart-container', style={'flex': '1', 'margin-right': '10px'}),
        html.Div([
            html.Label("Select Countries:", className='dropdown-label'),
            dcc.Dropdown(id='dropdown-total-country-streams', multi=True, className='dropdown', style={'width': '100%', 'display': 'inline-block'})
        ], className='dropdownchart-container', style={'flex': '1', 'margin-right': '10px'}),
        html.Div([
            html.Label("Select Date Range:", className='dropdown-label'),
            dcc.DatePickerRange(
                id='date-picker-total-streams-range',
                start_date_placeholder_text='Start Date',
                end_date_placeholder_text='End Date',
                display_format='YYYY-MM-DD',
                style={'width': '100%', 'display': 'inline-block'}
            ),
        ], className='dropdownchart-container', style={'flex': '1'}),
    ], style={'display': 'flex', 'align-items': 'center'}),
], className='graph-container'),

    html.Div([
        html.H2("Total Earnings", className='graph-heading'),
        dcc.Graph(id='total-earnings-chart', className='graph'),
        html.Div([
            # Dropdowns and Date Picker in one row
            html.Div([
                html.Label("Select Songs:", className='dropdown-label'),
                dcc.Dropdown(id='dropdown-total-song-earnings', multi=True, className='dropdown', style={'width': '100%', 'display': 'inline-block'})
            ], className='dropdownchart-container', style={'flex': '1', 'margin-right': '10px'}),
            html.Div([
                html.Label("Select Countries:", className='dropdown-label'),
                dcc.Dropdown(id='dropdown-total-country-earnings', multi=True, className='dropdown', style={'width': '100%', 'display': 'inline-block'})
            ], className='dropdownchart-container', style={'flex': '1', 'margin-right': '10px'}),
            html.Div([
                html.Label("Select Date Range:", className='dropdown-label'),
                dcc.DatePickerRange(
                    id='date-picker-total-earnings-range',
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date',
                    display_format='YYYY-MM-DD',
                    style={'width': '100%', 'display': 'inline-block'}
                ),
            ], className='dropdownchart-container', style={'flex': '1'}),
        ], style={'display': 'flex', 'align-items': 'center'}),
    ], className='graph-container'),
], className='p-5')

# Callback to parse uploaded file and update dropdown menus
@app.callback(
    [Output('dropdown-song', 'options'),
     Output('dropdown-store', 'options')],
    [Input('upload-data', 'contents')]
)
def update_dropdowns(contents):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        song_options = [{'label': title, 'value': title} for title in df['Title'].unique()]
        store_options = [{'label': store, 'value': store} for store in df['Store'].unique()]
        return song_options, store_options
    else:
        return [], []
    
# Callback to update dropdown options for Total Streams and Total Earnings charts
@app.callback(
    [Output('dropdown-total-song-streams', 'options'),
     Output('dropdown-total-country-streams', 'options'),
     Output('dropdown-total-song-earnings', 'options'),
     Output('dropdown-total-country-earnings', 'options')],
    [Input('upload-data', 'contents')]
)
def update_dropdowns_total(contents):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        
        # Filter out NaN values
        df = df.dropna(subset=['Title', 'Country of Sale'])
        
        song_options = [{'label': title, 'value': title} for title in df['Title'].unique()]
        country_options = [{'label': country, 'value': country} for country in df['Country of Sale'].unique()]
        
        return song_options, country_options, song_options, country_options
    else:
        return [], [], [], []

# Callback to update graph based on dropdown selection
@app.callback(
    [Output('graph-earnings-per-stream', 'figure'),
     Output('graph-description', 'children')],  # Add Output for graph description
    [Input('dropdown-song', 'value'),
     Input('dropdown-store', 'value'),
     Input('upload-data', 'contents')]
)
def update_graph(selected_songs, selected_store, contents):
    if contents is not None and selected_songs:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        
        if selected_store:
            filtered_df = df[df['Store'] == selected_store]
        else:
            filtered_df = df.copy()  # Select all stores if none is selected
        
        filtered_df = filtered_df[filtered_df['Title'].isin(selected_songs)]
        
        # Calculate average earnings per stream per song
        avg_earnings_per_stream = filtered_df.groupby('Title')['Earnings (USD)'].mean().reset_index()

        # Create bar chart
        fig = px.bar(avg_earnings_per_stream, x='Title', y='Earnings (USD)', 
                     title=f'Average Earnings per Stream ({selected_store if selected_store else "All Stores"})',
                     color='Title', color_discrete_sequence=px.colors.qualitative.Set1)
        
        # Construct graph description
        graph_description = f"The current graph displays the earnings per stream for these songs: {', '.join(selected_songs)} through {selected_store}."
        
        return fig, graph_description
    else:
        return {}, ""

# Callback to update world map graphs
@app.callback(
    [Output('total-streams-by-country-1', 'figure'),
     Output('total-streams-by-country-2', 'figure')],
    [Input('upload-data', 'contents')]
)
def update_country_graphs(contents):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        
        # Convert "Country of Sale" column to strings
        df['Country of Sale'] = df['Country of Sale'].astype(str)
        
        # Filter out invalid or unexpected values (e.g., NaNs, numbers, or strings with more than 2 characters)
        filtered_df = df[df['Country of Sale'].str.len() == 2]
        
        # Exclude 'OU' (Other/Unknown) and 'US' from the filtered data
        filtered_df = filtered_df[(filtered_df['Country of Sale'] != 'OU') & (filtered_df['Country of Sale'] != 'US')]
        
        # Convert country codes to full country names
        country_names = filtered_df['Country of Sale'].apply(lambda x: country_alpha2_to_country_name(x))
        
        # Add the full country names to the DataFrame
        filtered_df['Full Country Name'] = country_names
        
        # Group by country and sum the streams
        country_streams = filtered_df.groupby('Full Country Name')['Quantity'].sum().reset_index()

        # Create choropleth map for all countries except the US
        fig1 = go.Figure(data=go.Choropleth(
            locations=country_streams['Full Country Name'],
            z=country_streams['Quantity'],
            locationmode='country names',
            colorscale='Viridis',
            colorbar_title='Streams',
            name='Excluding US'
        ))

        fig1.update_layout(
            geo=dict(
                showcoastlines=True,
            ),
            title='World Map (Excluding US)'
        )

        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        
        # Convert "Country of Sale" column to strings
        df['Country of Sale'] = df['Country of Sale'].astype(str)
        
        # Filter out invalid or unexpected values (e.g., NaNs, numbers, or strings with more than 2 characters)
        filtered_df = df[df['Country of Sale'].str.len() == 2]
        
        # Exclude 'OU' (Other/Unknown) and 'US' from the filtered data
        filtered_df = filtered_df[(filtered_df['Country of Sale'] != 'OU')]
        
        # Convert country codes to full country names
        country_names = filtered_df['Country of Sale'].apply(lambda x: country_alpha2_to_country_name(x))
        
        # Add the full country names to the DataFrame
        filtered_df['Full Country Name'] = country_names
        
        # Group by country and sum the streams
        country_streams_wus = filtered_df.groupby('Full Country Name')['Quantity'].sum().reset_index()
        # Create choropleth map for the US only
        fig2 = go.Figure(data=go.Choropleth(
            locations=country_streams_wus['Full Country Name'],
            z=country_streams_wus['Quantity'],
            locationmode='country names',
            colorscale='Viridis',
            colorbar_title='Streams',
            name='US Only'
        ))

        fig2.update_layout(
            geo=dict(
                showcoastlines=True,
            ),
            title='World Map'
        )

        return fig1, fig2
    else:
        return {}, {}

# Callback to update total streams chart
@app.callback(
    Output('total-streams-chart', 'figure'),
    [Input('upload-data', 'contents'),
     Input('dropdown-total-song-streams', 'value'),
     Input('dropdown-total-country-streams', 'value'),
     Input('date-picker-total-streams-range', 'start_date'),
     Input('date-picker-total-streams-range', 'end_date')]
)
def update_total_streams_chart(contents, selected_songs, selected_countries, start_date, end_date):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))

        # Filter by selected songs and countries
        if selected_songs:
            df = df[df['Title'].isin(selected_songs)]
        if selected_countries:
            df = df[df['Country of Sale'].isin(selected_countries)]

        # Filter by date range
        if start_date and end_date:
            df = df[(df['Reporting Date'] >= start_date) & (df['Reporting Date'] <= end_date)]
        df = df.dropna(subset=['Reporting Date'])
        # Group by reporting date and song title, and aggregate streams
        grouped_df = df.groupby(['Reporting Date', 'Title'])['Quantity'].sum().reset_index()
        grouped_df = grouped_df.sort_values(by='Reporting Date', ascending = True)
        # Create the chart with different lines for each song
        fig = px.line(grouped_df, x='Reporting Date', y='Quantity', color='Title',
                      title='Total Streams by Date',
                      labels={'Reporting Date': 'Date', 'Quantity': 'Total Streams'})

        return fig
    else:
        return {}


# Callback to update total earnings chart
@app.callback(
    Output('total-earnings-chart', 'figure'),
    [Input('upload-data', 'contents'),
     Input('dropdown-total-song-earnings', 'value'),
     Input('dropdown-total-country-earnings', 'value'),
     Input('date-picker-total-earnings-range', 'start_date'),
     Input('date-picker-total-earnings-range', 'end_date')]
)
def update_total_earnings_chart(contents, selected_songs, selected_countries, start_date, end_date):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))

        # Filter by selected songs and countries
        if selected_songs:
            df = df[df['Title'].isin(selected_songs)]
        if selected_countries:
            df = df[df['Country of Sale'].isin(selected_countries)]

        # Filter by date range
        if start_date and end_date:
            df = df[(df['Reporting Date'] >= start_date) & (df['Reporting Date'] <= end_date)]
        df = df.dropna(subset=['Reporting Date'])
        # Group by reporting date and song title, and aggregate earnings
        grouped_df = df.groupby(['Reporting Date', 'Title'])['Earnings (USD)'].sum().reset_index()
        grouped_df = grouped_df.sort_values(by='Reporting Date', ascending = True)
        # Create the chart with different lines for each song
        fig = px.line(grouped_df, x='Reporting Date', y='Earnings (USD)', color='Title',
                      title='Total Earnings by Date',
                      labels={'Reporting Date': 'Date', 'Earnings (USD)': 'Total Earnings'})

        return fig
    else:
        return {}


if __name__ == '__main__':
    app.run_server(debug=True)
