import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")
payload_min, payload_max = spacex_df['Payload Mass (kg)'].agg(["min", "max"])

# Initialize Dash app
app = dash.Dash(__name__)

# Layout configuration
app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': site, 'value': site} for site in ['All Sites'] + spacex_df['Launch Site'].unique().tolist()],
        value='All Sites',
        placeholder="Select a Launch Site",
        searchable=True
    ),
    html.Br(),
    
    dcc.Graph(id='success-pie-chart'),
    html.Br(),
    
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 10000: '10000'},
        value=[payload_min, payload_max]
    ),
    
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    df = spacex_df if selected_site == 'All Sites' else spacex_df[spacex_df['Launch Site'] == selected_site]
    return px.pie(df, values='class', names='Launch Site' if selected_site == 'All Sites' else 'class',
                  title=f'Success Launches {"by Site" if selected_site == "All Sites" else f"for {selected_site}"}')

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if selected_site != 'All Sites':
        df = df[df['Launch Site'] == selected_site]
    return px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                      title=f'Payload vs. Outcome {"for All Sites" if selected_site == "All Sites" else f"for {selected_site}"}')

# Run server
if __name__ == '__main__':
    app.run_server(port=8060)
