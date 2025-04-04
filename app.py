from flask import Flask, request, render_template
import requests
from lxml import html
import time

app = Flask(__name__)

# Dictionary to store XPath for scraping data from tgju.org
data = {
    "طلای 18 عیار": {"xpath": '//*[@id="main"]/div[4]/div[3]/div[2]/table/tbody/tr[1]/td[1]', "unit": "ریال"},
    "طلای 24 عیار": {"xpath": '//*[@id="main"]/div[4]/div[3]/div[2]/table/tbody/tr[2]/td[1]', "unit": "ریال"},
    "سکه امامی": {"xpath": '//*[@id="coin-table"]/tbody/tr[1]/td[1]', "unit": "ریال"},
    "سکه بهار آزادی": {"xpath": '//*[@id="coin-table"]/tbody/tr[2]/td[1]', "unit": "ریال"},
    "نیم سکه": {"xpath": '//*[@id="coin-table"]/tbody/tr[3]/td[1]', "unit": "ریال"},
    "ربع سکه": {"xpath": '//*[@id="coin-table"]/tbody/tr[4]/td[1]', "unit": "ریال"},
    "سکه گرمی": {"xpath": '//*[@id="coin-table"]/tbody/tr[5]/td[3]', "unit": "ریال"},
    "مثقال طلا(مظنه)": {"xpath": '//*[@id="main"]/div[4]/div[4]/div[1]/table/tbody/tr[1]/td[1]', "unit": "ریال"},
}

# Weights for calculations
wonc = 31.103476
wseke = 8.13598
wnim = 4.0665
wrob = 2.03325
wmesghal = 4.6083

# Function to scrape price from tgju.org
def scrape_price(item):
    url = f"https://www.tgju.org/?t={int(time.time())}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    tree = html.fromstring(response.content)

    try:
        value = tree.xpath(data[item]["xpath"])[0].text_content().strip().replace(',', '')
        return int(float(value)) / 10  # Convert rial to toman
    except:
        return 0

# Function to calculate intrinsic value
def calculate_intrinsic_value(item, ponc, pdolar):
    if item == "طلای 18 عیار":
        return (ponc * pdolar * 1 * 750) / (1000 * wonc)
    elif item == "سکه امامی":
        return (ponc * pdolar * wseke * 900) / (1000 * wonc)
    elif item == "سکه بهار آزادی":
        return (ponc * pdolar * wseke * 900) / (1000 * wonc)
    elif item == "نیم سکه":
        return (ponc * pdolar * wnim * 900) / (1000 * wonc)
    elif item == "ربع سکه":
        return (ponc * pdolar * wrob * 900) / (1000 * wonc)
    elif item == "سکه گرمی":
        return (ponc * pdolar * 1 * 900) / (1000 * wonc)
    elif item == "مثقال طلا(مظنه)":
        return (ponc * pdolar * wmesghal * 705) / (1000 * wonc)
    elif item == "طلای 24 عیار":
        return (ponc * pdolar * 1 * 1000) / (1000 * wonc)
    return 0

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    ounce_price = request.form.get('ounce_price', '')
    dollar_price = request.form.get('dollar_price', '')
    selected_item = request.form.get('item', '')  # Default to empty string

    if request.method == 'POST':
        try:
            # Get user inputs
            ponc = float(ounce_price)
            pdolar = float(dollar_price)
            selected_item = request.form['item']

            # Scrape the price for the selected item
            price = scrape_price(selected_item)

            # Calculate intrinsic value
            intrinsic_value = calculate_intrinsic_value(selected_item, ponc, pdolar)

            # Calculate bubble, bubble percentage, and calculated dollar
            bubble = price - intrinsic_value if intrinsic_value != 0 else 0
            bubble_percentage = round(((price / intrinsic_value) - 1) * 100, 2) if intrinsic_value != 0 else 0
            calculated_dollar = (price * pdolar) / intrinsic_value if intrinsic_value != 0 else 0

            # Prepare the result
            result = {
                'item': selected_item,
                'price': f"{price:,.0f}",
                'intrinsic_value': f"{intrinsic_value:,.0f}" if intrinsic_value != 0 else "-",
                'bubble': f"{bubble:,.0f}" if bubble != 0 else "-",
                'bubble_percentage': f"{bubble_percentage:,.2f}" if bubble_percentage != 0 else "-",
                'calculated_dollar': f"{calculated_dollar:,.0f}" if calculated_dollar != 0 else "-",
                'ounce_price': f"{ponc:,.2f}",
                'dollar_price': f"{pdolar:,.0f}"
            }
        except Exception as e:
            result = {'error': f"خطا: {str(e)}"}

    return render_template('index.html', result=result, items=data.keys(), ounce_price=ounce_price, dollar_price=dollar_price, selected_item=selected_item)

if __name__ == '__main__':
    app.run(debug=True)