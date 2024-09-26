import pandas as pd
from datetime import datetime
from dash import Dash, html, dcc, Input, Output
from dash.dash_table import DataTable

# Load the dataset
df = pd.read_csv(r'C:\Users\lenovo\Desktop\NTProject\Combine_Exchange_Rate_Report_2012-2022 - Exchange_Rate_Report_2012.csv.csv')

# Ensure the 'Date' column is in datetime format and set it as the index
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%y', errors='coerce')
df.set_index('Date', inplace=True)

# Normalize the column names
df.columns = [col.strip().replace(' ', '_').replace('(', '').replace(')', '') for col in df.columns]

# Get unique currencies for dropdown
currencies = df.columns.tolist()

class FXRateService:
    def __init__(self, data_frame):
        self.data_frame = data_frame

    def get_fx_rates(self, base_currency, date):
        if not isinstance(date, datetime):
            raise ValueError("Date must be a datetime object.")
        
        date_str = date.strftime('%Y-%m-%d')
        print(f"Selected Date: {date_str}, Base Currency: {base_currency}")  # Debug statement

        try:
            rates_on_date = self.data_frame.loc[date]
        except KeyError:
            return None, f"No exchange rates found for {base_currency} on {date_str}"

        if base_currency not in rates_on_date.keys():
            return None, f"{base_currency} is not available in the dataset."

        base_rate = rates_on_date[base_currency]
        all_rates = {}

        for currency in rates_on_date.index:
            target_rate = rates_on_date[currency]
            if pd.notnull(target_rate):  # Ensure the rate is not NaN
                all_rates[currency] = base_rate / target_rate  # Calculate rate from target to base

        print("Fetched Rates:", all_rates)  # Debug statement
        return all_rates, None  # Return None for error message if no issues

# Initialize the Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Foreign Exchange Rate Converter", style={'textAlign': 'center', 'color': '#87CEEB', 'padding': '20px 0'}),  # Sky blue title

    # Center the dropdown and make it sky blue
    html.Div([
        html.Label("Select Base Currency:", style={'fontSize': '16px', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id='base-currency-dropdown',
            options=[{'label': currency.replace('_', ' '), 'value': currency} for currency in currencies],
            value='USD',  # Default value set to USD
            clearable=False,
            style={'width': '50%', 'margin': '0 auto', 'backgroundColor': 'skyblue'}  # Center and set sky blue background
        ),
    ], style={'textAlign': 'center', 'padding': '20px'}),

    html.Div([
        html.Label("Select Date:", style={'fontSize': '16px', 'marginBottom': '10px'}),
        dcc.DatePickerSingle(
            id='date-picker',
            date=datetime(2021, 1, 1),  # Default date
            display_format='YYYY-MM-DD',
            style={'marginBottom': '20px'}
        ),
        
        html.Button('Get FX Rates', id='get-rates-button', n_clicks=0, 
                    style={'backgroundColor': '#87CEEB', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 
                           'cursor': 'pointer', 'borderRadius': '5px'}),  # Sky blue button
    ], style={'textAlign': 'center', 'padding': '20px'}),

    html.Div([
        DataTable(id='fx-rates-table', columns=[], data=[], 
                  style_table={'overflowX': 'auto', 'margin': '20px auto', 'width': '80%'}, 
                  style_cell={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f9f9f9', 
                              'border': '1px solid #ddd'}),
        
        html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center', 'fontSize': '16px'})
    ], style={'padding': '10px 0'})
], style={'maxWidth': '1000px', 'margin': 'auto', 'backgroundColor': '#f4f4f4', 'borderRadius': '8px', 
          'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)', 'padding': '20px'})  # Removed the extra closing parenthesis here

@app.callback(
    Output('fx-rates-table', 'columns'),
    Output('fx-rates-table', 'data'),
    Output('error-message', 'children'),  # Output for error messages
    Input('get-rates-button', 'n_clicks'),
    Input('base-currency-dropdown', 'value'),
    Input('date-picker', 'date')
)
def update_fx_rates(n_clicks, base_currency, selected_date):
    if n_clicks > 0:
        date = pd.to_datetime(selected_date)
        fx_service = FXRateService(df)
        all_rates, error_message = fx_service.get_fx_rates(base_currency, date)

        if error_message:
            return [], [], error_message  # Return empty if there was an error
        
        # Prepare data for the DataTable
        if isinstance(all_rates, dict):
            rates_data = [{'Currency': currency.replace('_', ' '), 'Rate': round(rate, 6)} for currency, rate in all_rates.items()]
            columns = [{'name': 'Currency', 'id': 'Currency'}, {'name': 'Rate', 'id': 'Rate'}]
            return columns, rates_data, ""  # Clear error message if successful
        
    return [], [], ""  # Return empty if button not clicked

if __name__ == "__main__":
    app.run_server(debug=False)