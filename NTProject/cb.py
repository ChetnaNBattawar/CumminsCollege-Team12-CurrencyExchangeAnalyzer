import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests

# List of available currencies for selection
available_currencies = {
    "DZD": "Algerian dinar",
    "AUD": "Australian dollar",
    "BWP": "Botswana pula",
    "BRL": "Brazilian real",
    "BND": "Brunei dollar",
    "CAD": "Canadian dollar",
    "CLP": "Chilean peso",
    "CNY": "Chinese yuan",
    "CZK": "Czech koruna",
    "DKK": "Danish krone",
    "EUR": "Euro",
    "INR": "Indian rupee",
    "ILS": "Israeli New Shekel",
    "JPY": "Japanese yen",
    "KRW": "Korean won",
    "KWD": "Kuwaiti dinar",
    "MYR": "Malaysian ringgit",
    "MUR": "Mauritian rupee",
    "MXN": "Mexican peso",
    "NZD": "New Zealand dollar",
    "NOK": "Norwegian krone",
    "OMR": "Omani rial",
    "PEN": "Peruvian sol",
    "PHP": "Philippine peso",
    "PLN": "Polish zloty",
    "QAR": "Qatari riyal",
    "RUB": "Russian ruble",
    "SAR": "Saudi Arabian riyal",
    "SGD": "Singapore dollar",
    "ZAR": "South African rand",
    "SEK": "Swedish krona",
    "CHF": "Swiss franc",
    "THB": "Thai baht",
    "TTD": "Trinidadian dollar",
    "AED": "U.A.E. dirham",
    "GBP": "U.K. pound",
    "USD": "U.S. dollar",
    "UYU": "Uruguayan peso"
}

# Fetch exchange rates using CurrencyLayer API
def get_exchange_rates(api_key, base_currency):
    currencies_string = ','.join(available_currencies.keys())
    url = f"http://apilayer.net/api/live?access_key={api_key}&currencies={currencies_string}&source={base_currency}&format=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            quotes = data["quotes"]
            rates = {k.replace(base_currency, ""): v for k, v in quotes.items()}
            return rates
        else:
            raise ValueError(f"API Error: {data['error']['info']}")
    else:
        raise ConnectionError(f"Failed to connect to the API, Status code: {response.status_code}")

# Function to calculate basket value
def calculate_basket_value(basket, base_currency, api_key):
    rates = get_exchange_rates(api_key, base_currency)

    basket_value_in_base = 0
    for currency, amount in basket.items():
        if currency in rates:
            rate_to_base = rates[currency]
            basket_value_in_base += amount * rate_to_base
        else:
            print(f"Exchange rate for {currency} not found.")
    
    return basket_value_in_base

# Initialize the app
app = dash.Dash(__name__)

app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 'backgroundColor': '#f4f4f4'}, children=[
    html.H1("Custom Currency Basket", style={'textAlign': 'center', 'color': '#2c3e50'}),
    
    # Currency 1 input
    html.Div(style={'margin-bottom': '20px'}, children=[
        html.Label("Currency 1", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='currency1', options=[{'label': f"{code} - {name}", 'value': code} for code, name in available_currencies.items()], value='USD'),
        html.Label("Amount for Currency 1", style={'fontWeight': 'bold'}),
        dcc.Input(id='amount1', type='number', value=0, step=0.01, style={'width': '100%', 'padding': '10px', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
    ]),
    
    # Currency 2 input
    html.Div(style={'margin-bottom': '20px'}, children=[
        html.Label("Currency 2", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='currency2', options=[{'label': f"{code} - {name}", 'value': code} for code, name in available_currencies.items()], value='EUR'),
        html.Label("Amount for Currency 2", style={'fontWeight': 'bold'}),
        dcc.Input(id='amount2', type='number', value=0, step=0.01, style={'width': '100%', 'padding': '10px', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
    ]),
    
    # Currency 3 input
    html.Div(style={'margin-bottom': '20px'}, children=[
        html.Label("Currency 3", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='currency3', options=[{'label': f"{code} - {name}", 'value': code} for code, name in available_currencies.items()], value='JPY'),
        html.Label("Amount for Currency 3", style={'fontWeight': 'bold'}),
        dcc.Input(id='amount3', type='number', value=0, step=0.01, style={'width': '100%', 'padding': '10px', 'border': '1px solid #ccc', 'borderRadius': '4px'}),
    ]),
    
    # Base currency selection
    html.Div(style={'margin-bottom': '20px'}, children=[
        html.Label("Base Currency", style={'fontWeight': 'bold'}),
        dcc.Dropdown(id='base_currency', options=[{'label': f"{code} - {name}", 'value': code} for code, name in available_currencies.items()], value='INR'),
    ]),
    
    # Button to calculate the basket value
    html.Button('Calculate Basket Value', id='calculate-btn', style={'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer'}),
    html.Div(id='button-container', style={'textAlign': 'center', 'margin-top': '20px'}),
    
    # Display result
    html.Hr(),
    html.H3("Basket Value", style={'textAlign': 'center', 'color': '#2980b9'}),
    html.Div(id='basket_value', style={'margin-top': '20px', 'textAlign': 'center', 'fontSize': '24px', 'color': '#2c3e50'})
])

@app.callback(
    Output('basket_value', 'children'),
    Input('calculate-btn', 'n_clicks'),
    State('currency1', 'value'),
    State('currency2', 'value'),
    State('currency3', 'value'),
    State('amount1', 'value'),
    State('amount2', 'value'),
    State('amount3', 'value'),
    State('base_currency', 'value'),
)
def calculate_basket_value_callback(n_clicks, cur1, cur2, cur3, amt1, amt2, amt3, base):
    if n_clicks is None:
        return "Basket value will be shown here"

    # Prepare basket
    basket = {
        cur1: amt1,
        cur2: amt2,
        cur3: amt3
    }
    
    # Replace with your CurrencyLayer API key
    api_key = '413d262be359642528c82c4e3af35708'  # Replace with your actual API key
    
    # Calculate the basket's value in the base currency
    try:
        basket_value = calculate_basket_value(basket, base, api_key)
        return f"The value of the basket in {base} is: {basket_value:.2f}"
    except Exception as e:
        return str(e)

if __name__ == '__main__':
        app.run_server(debug=True)