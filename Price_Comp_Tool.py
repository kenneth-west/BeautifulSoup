from pandasgui import show
import requests
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
import json
from parsel import Selector
from collections import defaultdict
import pandas as pd
import sys
import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QLineEdit, QLabel

# GUI dev PyQT5

# pip install PyQt5
    
# Working Input Window

# The text is to be stored in this string
user_input = ''

def storeString(inString):
    """
    This function takes the user input and searches three websites, namely,
    Walmart, Amazon, and Kroger, for the requested item and scrapes name, price,
    ratings, and UPC code of the all the products that show up in search results.
    All this info is stored in a dataframe whichwill be shown as an output.

    Parameters
    ----------
    inString : user entered keyword as a string. It could be UPC code or item name

    Yields
    ------
    df: dataframe of name, price ratings, and UPC code of all the products found

    """
    
    global user_input
    user_input = inString
    user_input = user_input.replace(" ", "")
    
    # ScrapeOps Proxy Aggregator
    
    SCRAPEOPS_API_KEY = '0fc1ed7c-baed-4fd7-a75d-c3a610984185'
    
    def scrapeops_url(url):
        """
        
        The ScrapeOps Proxy Aggregator is a smart proxy that handles 
        everything for you:

        Proxy rotation & selection
        Rotating user-agents & browser headers
        Ban detection & CAPTCHA bypassing
        Country IP geotargeting
        Javascript rendering with headless browsers
        
        To use the ScrapeOps Proxy Aggregator, we just need to send the 
        URL we want to scrape to the Proxy API instead of making the 
        request directly ourselves. This a simple wrapper function.
        
        Parameters
        ----------
        url : URL of website that needs to be scrapped

        Returns
        -------
        proxy_url : Disguised url
            
        """
        payload = {'api_key': SCRAPEOPS_API_KEY, 'url': url, 'country': 'us'}
        proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
        return proxy_url
    
    # UPC Converter

    def upc_converter(upc_code):
        
        """
        This function takes in 12 digit upc code as a string and 
        gives you item name as a string using barcode spider website.
        
        NOTE: This function was created so that we can search for the item in
        Walmart item since they don't use UPC code.
        
        Parameters
        ----------
        upc_code : 12 digit UPC code of the item who's price needs to be compared'

        Returns
        -------
        Item name as a string

        """
        url = 'https://www.barcodespider.com/' + upc_code
        response = requests.get(scrapeops_url(url))
        item_name = ''
        if upc_code.isnumeric() == True:
            # Check is entered input is UPC code or not
            # If it is UPC code - barcode spider will be scrapped to find out 
            # name of the item
            # If entered input is not all numbers - same user input will be 
            # output of this function
            if response.status_code == 200:
                html_response = response.text
                
                # Request was used to get the data and it will be parsed using
                # beautiful soup
                soup = BeautifulSoup(html_response, "html.parser")
            
                script_tag = soup.find("div", {"class": "detailtitle"})
                item_name = script_tag.h2.get_text()
            elif response.status_code == 404:
                print('UPC code not found on Barcode Spider')
        else:
            item_name = upc_code
        
        return item_name

    # Walmart Web Scrapping

    def walmart(keyword):
        """
        This function will search for the item user is requesting and scrap 
        information of all the items found on page 1.
        
        Note: Walmart doesn't use UPC code so input has to name of the item or 
        else it will yield zero search results.
        
        Once search result shows items, URL of all the items will be collected
        and one by one we'll go to each URL and scrape Name, Price and Rating
        information in as list of dictionary.
        
        This approach of going to each items URL was used because plan was to 
        scrape more info such as brand name, ID, manufacturing name, short 
        description of the prodcut butlater on plan was changed to only show 
        name, price, and rating.

        Parameters
        ----------
        keyword : User input if its not all numeric OR output from upc_converter
        function

        Returns
        -------
        walmart_data_list: List of dictionary which will contain Name, Price,
        and Rating of the products found
        
        """
        
        def create_walmart_product_url(product):
            """
            Creating URL of the product found in our search results so that we
            can later use it to scrape required info.

            """
            return 'https://www.walmart.com' + product.get('canonicalUrl', '').split('?')[0]
        
        headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
        product_url_list = []
        
        # Loop Through Walmart Page 1 Until No More Products
        for page in range(1,2):
            try:
                payload = {'q': keyword, 'sort': 'best_seller', 'page': page, 'affinityOverride': 'default'}
                walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
                response = requests.get(scrapeops_url(walmart_search_url), headers=headers)
                
                # Request will be used to get the data and it will be parsed using
                # beautiful soup
                # Required info can be extracted easily as the data is available 
                # as hidden JSON data on the page.
                
                if response.status_code == 200:
                    html_response = response.text
                    soup = BeautifulSoup(html_response, "html.parser")
                    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
                    
                    if script_tag is not None:
                        json_blob = json.loads(script_tag.get_text())
                        product_list = json_blob["props"]["pageProps"]["initialData"]["searchResult"]["itemStacks"][0]["items"]
                        product_urls = [create_walmart_product_url(product) for product in product_list]
                        product_url_list.extend(product_urls)
                        if len(product_urls) == 0:
                            break
                            
            except Exception as e:
                print('Error', e)
        
        walmart_data_list = []
                    
        ## Loop Through Walmart Product URL List to scrape required info
        for url in product_url_list:
            try:
                response = requests.get(scrapeops_url(url))
                
                # Request will be used to get the data and it will be parsed using
                # beautiful soup
                # Required info can be extracted easily as the data is available 
                # as hidden JSON data on the page.
        
                if response.status_code == 200:
                    html_response = response.text
                    soup = BeautifulSoup(html_response, "html.parser")
                    script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
                    if script_tag is not None:
                        json_blob = json.loads(script_tag.get_text())
                        raw_product_data = json_blob["props"]["pageProps"]["initialData"]["data"]["product"]
                        walmart_data_list.append({
                            'Name': raw_product_data.get('name'),
                            'Price': raw_product_data['priceInfo']['currentPrice'].get('price'),
                            'Rating': raw_product_data.get('averageRating'),
                            })
                            
            except Exception as e:
                print('Error', e)            
            
        return walmart_data_list

    # Amazon Web Scrapping

    def amazon(user_input1):
        """
        This function will search amazon website for the item user requested.
        After that, selector is used to get the necessary data from the search
        results of each item that shows up in search results which helps to
        extract name, price, rating, and UPC code easily.

        Parameters
        ----------
        user_input1 : User input as a string. Could be item name or UPC code

        Returns
        -------
        amazon_data_list: List of dictionary which will contain Name, Price,
        Rating, and UPC code of the products found

        """
        
        keyword_list = [user_input1]
        amazon_data_list = []
        
        for keyword in keyword_list:
            url_list = [f'https://www.amazon.com/s?k=%7B{keyword}%7D&page=1']
            for url in url_list:
                try:
                    response = requests.get(scrapeops_url(url))
        
                    if response.status_code == 200:
                        sel = Selector(text=response.text)
        
                        ## Extract Product Data From Search Page
                        search_products = sel.css("div.s-result-item[data-component-type=s-search-result]")
                        for product in search_products:
                            relative_url = product.css("h2>a::attr(href)").get()
                            UPC = relative_url.split('keywords=')[1][:12] if len(relative_url.split('keywords=')) >= 1 else None
                            if UPC.isnumeric() == False:
                                UPC = 'None'
                            amazon_data_list.append(
                                {
                                    "Name": product.css("h2>a>span::text").get(),
                                    "Price": product.css(".a-price[data-a-size=xl] .a-offscreen::text").get(),
                                    "Rating": (product.css("span[aria-label~=stars]::attr(aria-label)").re(r"(\d+.\d) out") or [None])[0],
                                    "UPC": UPC,
                                }
                            )
        
                except Exception as e:
                    print("Error", e)
        
        return amazon_data_list

    # Kroger Web Scrapping

    def kroger(keyword):
        """
        Kroger website will searched for the item user has requested and name
        and price will be extracted.

        Parameters
        ----------
        keyword : user input as a string - could be item name or UPC code

        Returns
        -------
        kroger_data_list: List of dictionary which will contain Name and Price 
        of the products found

        """
        
        # Scrape the url using Scrapeops
        def scrapeops_url(url):
            payload = {
                "api_key": SCRAPEOPS_API_KEY,
                "url": url,
                "country": "us",
                "DOWNLOAD_DELAY": 2,
            }
            proxy_url = "https://proxy.scrapeops.io/v1/?" + urlencode(payload)
            return proxy_url
        
        # Final url
        product_url_list_krog = [
            f"https://www.kroger.com/search?query={keyword}&searchType=default_search"
        ]
        
        
        kroger_data_list = []
        
        ## Loop Through kroger_data_list Product URL List
        for urlkr in product_url_list_krog:
            # Runs until correct data is found
            success = False
            ##Runs the code 5 times to try and scrape accurate data
            for attempts in range(0, 5):
                # If its successful the for loop breaks
                if success:
                    break
                # Helps keep track of attempts
                print("Attempt to contact " + str(attempts))
                response_kr = requests.get(scrapeops_url(urlkr))
                # If the website has full processed continue with grabbing data
                if response_kr.status_code == 200:
                    # Pull text from website
                    html_response = response_kr.text
                    # pull text and make html using beautifulsoup
                    soup = BeautifulSoup(html_response, "html.parser")
                    # Create a script that has all needed info
                    script_tag = soup.find(
                        "div", {"class": "ProductGridContainer md:px-0"}
                    )
        
                    # If script_tag is successful continue if not rerun website scrape
                    if script_tag is not None:
                        # for loop thorugh Length of items on page
                        for s in script_tag.find_all(
                            "div", {"class": "AutoGrid-cell min-w-0"}
                        ):
                            # Pulls the name of the item
                            name = s.find(
                                "h3",
                                {
                                    "class": "kds-Text--l text-primary font-secondary font-medium my-8"
                                },
                            ).get_text()
                            # Extra gives information like oz or pounds of item if applicable
                            
                            if (s.find("span",{"class": "kds-Text--s text-neutral-more-prominent"},)== None):
                                continue
                            else:
                                extra = s.find("span",{"class": "kds-Text--s text-neutral-more-prominent"},).get_text()
                            # Price of item with discounted price
                            
                            if (s.find("div",{"class": "flex justify-between items-center mb-8 mt-24"},)== None):
                                continue
                            else:
                                price = s.find("div",{"class": "flex justify-between items-center mb-8 mt-24"},).get_text()
                                
                            
                            # price = s.find(
                            #     "div",
                            #     {
                            #         "class": "flex justify-between items-center mb-8 mt-24"
                            #     },
                            # ).get_text()
                            if price == "Prices May Vary":
                                price = "NA"
                            # Append list with name and price
                            kroger_data_list.append(
                                {
                                    # Add extra to the name to help be more specifc
                                    "Name": name + " " + extra,
                                    # Split the original price from the current price
                                    "Price": price.split(" ")[0],
                                }
                            )
                            
                        # If itms are scraped terminate the for loop by success = True
                        success = True
        
        return kroger_data_list

    # Data analysis

    def Dict2pandas(Store, name):
        """
        Change the tuple into a list of dictionaries before putting into pandas

        Args:   p1 (dict): First variable
                p2 (str): Name of the store to be added to dict

        Returns:   d (data frame): updated pandas data frame

        """
        # Create list to help convert to pandas
        lst = defaultdict(list)
        # Run through each dictionary in the tuple and add to list
        for d in Store:
            # Cycle through all keys and values in the dictionary
            for key, value in d.items():
                # Add each dictionary to the list
                lst[key].append(value)
        # Create pandas data frame from the dictionary list
        ste = pd.DataFrame.from_dict(lst)
        # Add in the store name for each column for easy comparison
        ste["Store Name"] = name

        return ste


    # Name of stores
    name = ["Walmart", "Amazon", "Kroger"]

    # Create the pandas for each store
    walmart_key = upc_converter(user_input)
    amazonData = amazon(user_input)
    krogerData = kroger(user_input)
    
    # Checking if amazon and kroger output was an empty list or not
    if len(amazonData) > 0:
        Ama = Dict2pandas(amazonData, name[1])
    else: 
        Ama = []
    
    if len(krogerData) > 0:
        Krog = Dict2pandas(krogerData, name[2])
    else:
        Krog = []
    
    Wal = Dict2pandas(walmart(walmart_key), name[0])
    # Ama = Dict2pandas(amazon(user_input), name[1])
    # Krog = Dict2pandas(kroger(user_input), name[2])
    # Adjust the price and rating of each item into a float
    # Krog["Price"] = pd.to_numeric(Krog["Price"], errors="coerce")
    # Ama["Price"] = pd.to_numeric(Ama["Price"], errors="coerce")
    # Ama["Rating"] = pd.to_numeric(Ama["Rating"], errors="coerce")

    # Create a list of the data frames to help combine them
    frames = []
    for it in [Wal, Ama, Krog]:
        if len(it) > 0:
            frames.append(it)
    
    # frames = [Wal, Ama, Krog]
    # Combined all three data frames
    df = pd.concat(frames)
    # Group them by the title name
    # s = df.groupby(["Name", "Store Name"])["Price"].min()
    # print(s)
    # Do something with the string
    
    return show(df)

###############################################################################

# For passing the string to some function in another file:
# from StringStorage import storeString

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'WebScraper'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 200
        self.initUI()
        self.close

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Create Label
        self.label = QLabel('Item Name/Descriptor:', self)
        self.label.move(20, 55)
        
        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 75)
        self.textbox.resize(280,40)

        # Create a button in the window
        self.button = QPushButton('Run', self)
        self.button.move(300, 75)
        self.button.resize(80,40)

        # When the 'clicked' signal of the button is emitted, call some function (which acts as a slot):
        self.button.clicked.connect(self.onButtonClicked)
        self.button.clicked.connect(self.close)

        self.show()
        

    # Function to pass the entered string along to the function from another file
    def onButtonClicked(self):
        storeString(self.textbox.text())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())