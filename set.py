from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Headers for Flipkart and Amazon
headers_flip = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}

headers_amaz = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
}

# Function to scrape Flipkart
def flip_prize(product, Flag):
    url = 'https://www.flipkart.com/search?q=' + product
    response = requests.get(url, headers=headers_flip)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_box = soup.find_all('div', {"class": "_1AtVbE"})  # Updated class for product container
    temp = []
    try:
        for box in main_box:
            product_link = box.find("a", {"class": "_1fQZEK"}, href=True)  # Updated class for product link
            if product_link:
                s = "https://www.flipkart.com"
                link = s + product_link['href']
                title = box.find("div", {"class": "_4rR01T"}).text.strip()  # Updated class for product title
                price = box.find("div", {"class": "_30jeq3 _1_WHN1"}).text.strip()  # Updated class for price
                product_img = box.find("img", {"class": "_396cs4"}).get('src')  # Updated class for image
                if Flag:
                    temp.append([link, product_img, title, price])
                else:
                    if product.lower() in title.lower():
                        temp.append([link, product_img, title, price])
    except Exception as e:
        print(f"Error scraping Flipkart: {e}")
    return temp

# Function to scrape Amazon
def amaz_price(product, Flag):
    url = "https://www.amazon.in/s?k=" + product
    response = requests.get(url, headers=headers_amaz)
    soup = BeautifulSoup(response.text, 'html.parser')
    main_box = soup.find_all('div', {"class": "s-result-item"})  # Updated class for product container
    temp = []
    try:
        for box in main_box:
            product_link = box.find("a", {"class": "a-link-normal s-no-outline"}, href=True)  # Updated class for product link
            if product_link:
                s = "https://www.amazon.in"
                link = s + product_link['href']
                title = box.find("span", {"class": "a-size-medium a-color-base a-text-normal"}).text.strip()  # Updated class for title
                price = box.find("span", {"class": "a-price-whole"})  # Updated class for price
                if price:
                    price = price.text.strip()
                else:
                    price = "N/A"
                product_img = box.find("img", {"class": "s-image"}).get('src')  # Updated class for image
                if Flag:
                    temp.append([link, product_img, title, price])
                else:
                    if product.lower() in title.lower():
                        temp.append([link, product_img, title, price])
    except Exception as e:
        print(f"Error scraping Amazon: {e}")
    return temp

# Main route
@app.route('/')
def main():
    return render_template('index.html')

# Route to handle search
@app.route('/getValue', methods=['POST'])
def getValue():
    words = ["under", "below", "above", "new", "phones", "mobiles", "laptops"]
    product_name = request.form['proName']
    choice = request.form['choice']
    Flag = False
    for word in words:
        if word in product_name:
            Flag = True
            break

    if choice == "tech":
        flip_list = flip_prize(product_name, Flag)
        amaz_list = amaz_price(product_name, Flag)
        return render_template('pass.html', p=product_name, li=flip_list, li_amaz=amaz_list)
    else:
        flip_list = flip_prize(product_name, Flag)
        amaz_list = amaz_price(product_name, Flag)
        return render_template('passother.html', p=product_name, li=flip_list, li_amaz=amaz_list)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)