from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objs as go

app = Dash(__name__)

# Load the dataset
file_path = 'C:\\Users\\lenovo\\Desktop\\NTProject\\Combine_Exchange_Rate_Report_2012-2022.xlsx'
df = pd.read_excel(file_path)

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Set 'Date' as the index
df.set_index('Date', inplace=True)

# Sample currency list for the dropdown (using only relevant currencies)
currency_list = df.columns.tolist()  # Get column names from the dataset

app.layout = html.Div([
    html.H1("Currency Converter"),
    
    html.Div([
        html.Label("Select Currency to Convert From:"),
        dcc.Dropdown(id='currency-from-dropdown', options=[{'label': currency, 'value': currency} for currency in currency_list], value='U.S. dollar (USD)'),
        
        html.Label("Select Currency to Convert To:"),
        dcc.Dropdown(id='currency-to-dropdown', options=[{'label': currency, 'value': currency} for currency in currency_list], value='Australian dollar (AUD)'),
        
        html.Label("Enter Amount:"),
        dcc.Input(id='amount-input', type='number', placeholder='Enter amount', min=0),
        
        html.Label("Select Time Granularity:"),
        dcc.Dropdown(id='granularity-dropdown', 
                     options=[
                         {'label': 'Quarterly', 'value': 'Q'},
                         {'label': 'Weekly', 'value': 'W'},
                         {'label': 'Monthly', 'value': 'M'},
                         {'label': 'Yearly', 'value': 'Y'}
                     ],
                     value='Q'),  # Default value is Quarterly
        
        html.Label("Select Date Range:"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=pd.to_datetime('2012-01-01'),
            end_date=pd.to_datetime('2022-12-31'),
            display_format='YYYY-MM-DD',
            min_date_allowed=pd.to_datetime('2012-01-01'),  # Set minimum date
            max_date_allowed=pd.to_datetime('2022-12-31')   # Set maximum date
        ),
        
        html.Button('Convert', id='convert-button'),
        dcc.Graph(id='conversion-graph'),
        html.Div(id='result-output', style={'margin-top': '20px'})
    ]),
    
    html.Div([
        html.H2("Currency Volatility Indicator"),
        
        html.Label("Select Currency 1:"),
        dcc.Dropdown(
            id='currency1-dropdown',
            options=[{'label': col, 'value': col} for col in currency_list],
            value='U.S. dollar (USD)'  # Default value
        ),
        
        html.Label("Select Currency 2:"),
        dcc.Dropdown(
            id='currency2-dropdown',
            options=[{'label': col, 'value': col} for col in currency_list],
            value='Australian dollar (AUD)'  # Default value
        ),
        
        html.Label("Select Volatility Date Range:"),
        dcc.DatePickerRange(
            id='volatility-date-picker-range',
            start_date=pd.to_datetime('2012-01-01'),
            end_date=pd.to_datetime('2022-12-31'),
            display_format='YYYY-MM-DD',
            min_date_allowed=pd.to_datetime('2012-01-01'),
            max_date_allowed=pd.to_datetime('2022-12-31')
        ),
        
        dcc.Graph(id='volatility-graph'),
        html.Div(id='risk-output', style={'margin-top': '20px'})
    ])
])

@app.callback(
    Output('conversion-graph', 'figure'),
    Output('result-output', 'children'),
    Input('convert-button', 'n_clicks'),
    State('currency-from-dropdown', 'value'),
    State('currency-to-dropdown', 'value'),
    State('amount-input', 'value'),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('granularity-dropdown', 'value')
)
def update_output(n_clicks, currency_from, currency_to, amount, start_date, end_date, granularity):
    if n_clicks is None or amount is None or amount <= 0:
        return go.Figure(), 'Please fill in all fields and press Convert.'

    # Filter the dataframe for the selected date range
    filtered_data = df.loc[start_date:end_date]

    # Check if the currencies are in the dataframe
    if currency_from not in filtered_data.columns or currency_to not in filtered_data.columns:
        return go.Figure(), f"Currency '{currency_from}' or '{currency_to}' not found in the dataset."

    # Ensure there is data in the filtered range
    if filtered_data.empty:
        return go.Figure(), f"No data available for the selected date range."

    # Calculate conversion based on actual rates
    filtered_data['Converted'] = filtered_data[currency_to] / filtered_data[currency_from] * amount

    # Resample the data based on the user-selected granularity
    resampled_data = filtered_data['Converted'].resample(granularity).mean()

    # Check if resampled data is empty
    if resampled_data.empty:
        return go.Figure(), f"No data available for the selected granularity in the date range."

    # Calculate min and max values
    min_value = resampled_data.min()
    max_value = resampled_data.max()
    min_date = resampled_data.idxmin()
    max_date = resampled_data.idxmax()

    # Create the graph
    figure = go.Figure(data=[
        go.Scatter(
            x=resampled_data.index, 
            y=resampled_data, 
            mode='lines+markers', 
            name=f'{amount} {currency_from} to {currency_to}',
            hovertemplate=
            'Date: %{x}<br>' +
            'Converted Amount: %{y:.2f}<br>' +
            'Actual Amount: ' + str(amount) + ' ' + currency_from + '<extra></extra>',
            line=dict(color='blue'),  # Main line color
            marker=dict(color='blue')  # Main marker color
        ),
        go.Scatter(
            x=[min_date], 
            y=[min_value], 
            mode='markers+text',
            marker=dict(color='red', size=10),
            name='Minimum Value',
            text=f'Min: {min_value:.2f}',
            textposition='top center'
        ),
        go.Scatter(
            x=[max_date], 
            y=[max_value], 
            mode='markers+text',
            marker=dict(color='green', size=10),
            name='Maximum Value',
            text=f'Max: {max_value:.2f}',
            textposition='top center'
        )
    ])
    
    # Adding min and max values as text boxes in the corner
    figure.add_annotation(
        xref='paper',
        yref='paper',
        x=0.95,
        y=0.95,
        text=f'Min Value: {min_value:.2f}<br>Max Value: {max_value:.2f}',
        showarrow=False,
        font=dict(size=12, color='black'),
        bgcolor='lightgray',
        bordercolor='black',
        borderwidth=1,
        borderpad=5
    )

    figure.update_layout(title=f'Conversion of {amount} {currency_from} to {currency_to} Over Time',
                         xaxis_title='Date',
                         yaxis_title=f'Amount in {currency_to}',
                         template='plotly')

    return figure, f'Converted {amount} {currency_from} to {currency_to} over the date range from {start_date} to {end_date}.<br>' + \
                   f'Min Value: {min_value:.2f}<br>Max Value: {max_value:.2f}'

@app.callback(
    Output('volatility-graph', 'figure'),
    Output('risk-output', 'children'),
    Input('currency1-dropdown', 'value'),
    Input('currency2-dropdown', 'value'),
    Input('volatility-date-picker-range', 'start_date'),
    Input('volatility-date-picker-range', 'end_date')
)
def update_volatility_graph(currency1, currency2, start_date, end_date):
    # Filter data for selected currencies and date range
    filtered_df = df.loc[start_date:end_date]

    # Calculate fluctuations
    filtered_df['Fluctuation'] = abs(filtered_df[currency1] - filtered_df[currency2])

    # Define risk thresholds
    low_threshold = 0.5  # Adjust these values based on your dataset
    high_threshold = 2.0

    # Determine risk level and assign color
    filtered_df['Risk'] = filtered_df['Fluctuation'].apply(
        lambda x: 'Low Risk' if x <= low_threshold else ('Medium Risk' if x <= high_threshold else 'High Risk')
    )

    filtered_df['Color'] = filtered_df['Risk'].map({
        'Low Risk': 'green',
        'Medium Risk': 'orange',
        'High Risk': 'red'
    })

    # Create the volatility graph with colored points based on risk
    figure = go.Figure()

    figure.add_trace(go.Scatter(
        x=filtered_df.index,
        y=filtered_df['Fluctuation'],
        mode='lines+markers',
        name='Fluctuation',
        marker=dict(color=filtered_df['Color'], size=8),
        line=dict(color='blue'),  # Line stays blue
        hovertemplate='Date: %{x}<br>Fluctuation: %{y:.2f}<extra></extra>'
    ))

    # Calculate and show risk count
    risk_count = filtered_df['Risk'].value_counts()
    risk_text = f"Risk Levels: Low Risk: {risk_count.get('Low Risk', 0)}, Medium Risk: {risk_count.get('Medium Risk', 0)}, High Risk: {risk_count.get('High Risk', 0)}"

    figure.update_layout(title=f'Volatility Between {currency1} and {currency2}',
                         xaxis_title='Date',
                         yaxis_title='Fluctuation',
                         template='plotly')

    return figure, risk_text


if __name__ == '__main__':
    app.run_server(debug=True)


   

