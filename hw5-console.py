import aiohttp
import asyncio
import sys
import certifi
import ssl
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"

async def fetch_exchange_rates(date: str) -> dict:
    url = API_URL.format(date=date)
    try:
        connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL/TLS to use custom SSL context

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data
    except aiohttp.ClientError as e:
        print(f"Error fetching data for {date}: {e}")
        return None

async def get_currency_rates(days: int, currencies: list) -> list:
    today = datetime.now().date()
    date_format = "%d.%m.%Y"
    currency_rates = []

    for i in range(days):
        date = (today - timedelta(days=i)).strftime(date_format)
        data = await fetch_exchange_rates(date)

        if data and 'exchangeRate' in data:
            rates = {
                date: {currency: {
                    'sale': next((rate['saleRate'] for rate in data['exchangeRate'] if rate['currency'] == currency), None),
                    'purchase': next((rate['purchaseRate'] for rate in data['exchangeRate'] if rate['currency'] == currency), None)
                } for currency in currencies}
            }
            currency_rates.append(rates)
        else:
            print(f"No data available for {date}")

    return currency_rates

def print_currency_rates(currency_rates: list):
    for rate in currency_rates:
        for date, currencies in rate.items():
            print(f"{date}:")
            for currency, values in currencies.items():
                print(f"  {currency}:")
                print(f"    Sale: {values['sale']}")
                print(f"    Purchase: {values['purchase']}")
            print("")

async def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        print("Usage: python main.py <number_of_days> [<currency1> <currency2> ...]")
        return

    days = int(sys.argv[1])
    if days > 10:
        print("Maximum number of days is 10")
        return

    currencies = sys.argv[2:] if len(sys.argv) > 2 else ['EUR', 'USD']  # Default to EUR and USD if no currencies provided
    currency_rates = await get_currency_rates(days, currencies)
    print_currency_rates(currency_rates)

if __name__ == '__main__':
    asyncio.run(main())

