import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import base64
import io
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout of the app with styling
app.layout = dbc.Container([
    html.Div([
        html.Div([
            html.H1('Snapshot: Data Visualization', className='header')
        ], className='header-container')
    ]),
    html.Div([
        html.Div([
            html.H2("Upload CSV File", className='upload-heading'),
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
        ], className='banner-container')
    ]),
    html.Div([
        html.Label("Select Songs Below:", className='dropdown-label'),
        dcc.Dropdown(id='dropdown-song', multi=True, className='dropdown')
    ], className='dropdown-container'),
    html.Div([
        dcc.Graph(id='graph-earnings-per-stream', className='graph')
    ], className='graph-container')
], className='p-5')

# Callback to parse uploaded file and update dropdown menu
@app.callback(
    Output('dropdown-song', 'options'),
    [Input('upload-data', 'contents')]
)
def update_dropdown(contents):
    if contents is not None:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        options = [{'label': title, 'value': title} for title in df['Title'].unique()]
        return options
    else:
        return []

# Callback to update graph based on dropdown selection
@app.callback(
    Output('graph-earnings-per-stream', 'figure'),
    [Input('dropdown-song', 'value'),
     Input('upload-data', 'contents')]
)
def update_graph(selected_songs, contents):
    if contents is not None and selected_songs:
        content_type, content_string = contents[0].split(',')
        df = pd.read_csv(io.StringIO(base64.b64decode(content_string).decode('utf-8')))
        
        fig = px.bar()
        for selected_song in selected_songs:
            # Filter dataframe based on selected song
            filtered_df = df[df['Title'] == selected_song]
            
            # Calculate average earnings per stream
            avg_earnings_per_stream = filtered_df['Earnings (USD)'].sum() / filtered_df['Quantity'].sum()
            
            # Update figure with new bar
            fig.add_bar(x=[selected_song], y=[avg_earnings_per_stream], name=selected_song)
        
        fig.update_layout(title='Average Earnings per Stream for Selected Songs', xaxis_title='Song', yaxis_title='Average Earnings per Stream', plot_bgcolor='#f8f9fa', paper_bgcolor='#f8f9fa', font_color='#343a40')
        return fig
    else:
        return {}

if __name__ == '__main__':
    app.run_server(debug=True)
