from pandasgui import show

def pricecomp(user_input):
    # UPC Converter

    def upc_converter(upc_code):
        
        import requests
        from urllib.parse import urlencode, urljoin
        from bs4 import BeautifulSoup
        
        SCRAPEOPS_API_KEY = 'c6f066cd-bae7-42e7-b96c-e5c44fd2d69d'
        
        def scrapeops_url(url):
            payload = {'api_key': SCRAPEOPS_API_KEY, 'url': url, 'country': 'us'}
            proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
            return proxy_url
        
        # keyword = '013000001243'
        
        url = 'https://www.barcodespider.com/' + upc_code
           
        response = requests.get(scrapeops_url(url))
        if response.status_code == 200:
                     
            html_response = response.text
            soup = BeautifulSoup(html_response, "html.parser")
            
            script_tag = soup.find("div", {"class": "detailtitle"})
            item_name = script_tag.h2.get_text()
        
        return item_name

    ###########################################################################################################
    # Walmart Web Scrapping

    walmart_key = upc_converter(user_input)

    def walmart(keyword):
        import json
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urlencode
        
        SCRAPEOPS_API_KEY = 'c6f066cd-bae7-42e7-b96c-e5c44fd2d69d'
        
        def scrapeops_url(url):
            payload = {'api_key': SCRAPEOPS_API_KEY, 'url': url, 'country': 'us'}
            proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
            return proxy_url
        
        def create_walmart_product_url(product):
            return 'https://www.walmart.com' + product.get('canonicalUrl', '').split('?')[0]
        
        headers={"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
        product_url_list = []
        
        # keyword = 'HeinzTomatoKetchup,14Ounce'
        
        ## Loop Through Walmart Pages Until No More Products
        for page in range(1,2):
            try:
                payload = {'q': keyword, 'sort': 'best_seller', 'page': page, 'affinityOverride': 'default'}
                walmart_search_url = 'https://www.walmart.com/search?' + urlencode(payload)
                response = requests.get(scrapeops_url(walmart_search_url), headers=headers)
                # print(response.status_code)
                
                
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
        
        ## Loop Through Walmart Product URL List
        for url in product_url_list:
            try:
                response = requests.get(scrapeops_url(url))
        
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

    ###########################################################################################################
    # Amazon Web Scrapping

    def amazon(user_input):
        
        import requests
        from parsel import Selector
        from urllib.parse import urlencode, urljoin
        
        SCRAPEOPS_API_KEY = 'c6f066cd-bae7-42e7-b96c-e5c44fd2d69d'
        
        def scrapeops_url(url):
            payload = {'api_key': SCRAPEOPS_API_KEY, 'url': url, 'country': 'us'}
            proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
            return proxy_url
        
        keyword_list = [user_input]
        # keyword_list = ['013000006057']
        amazon_data_list = []
        
        for keyword in keyword_list:
            url_list = [f'https://www.amazon.com/s?k=%7Bkeyword%7D&page=1']
            for url in url_list:
                try:
                    response = requests.get(scrapeops_url(url))
        
                    if response.status_code == 200:
                        sel = Selector(text=response.text)
        
                        ## Extract Product Data From Search Page
                        search_products = sel.css("div.s-result-item[data-component-type=s-search-result]")
                        for product in search_products:
                            relative_url = product.css("h2>a::attr(href)").get()
                            # asin = relative_url.split('/')[3] if len(relative_url.split('/')) >= 4 else None
                            UPC = relative_url.split('keywords=')[1][:12] if len(relative_url.split('keywords=')) >= 1 else None
                            # product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
                            amazon_data_list.append(
                                {
                                    "Name": product.css("h2>a>span::text").get(),
                                    "Price": product.css(".a-price[data-a-size=xl] .a-offscreen::text").get(),
                                    "Rating": (product.css("span[aria-label~=stars]::attr(aria-label)").re(r"(\d+.\d) out") or [None])[0],
                                    # "asin": asin,
                                    # "url": product_url,
                                    "UPC": UPC,
                                }
                            )
        
                except Exception as e:
                    print("Error", e)
        
        return amazon_data_list

    ###########################################################################################################
    # Kroger Web Scrapping

    def kroger(keyword):
        
        import json
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urlencode
        
        
        SCRAPEOPS_API_KEY = "0fc1ed7c-baed-4fd7-a75d-c3a610984185"
        
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
        
        
        ## kroger_data_list Search Keyword
        # keyword = ["0001300000640"]
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
                            extra = s.find(
                                "span",
                                {"class": "kds-Text--s text-neutral-more-prominent"},
                            ).get_text()
                            # Price of item with discounted price
                            price = s.find(
                                "div",
                                {
                                    "class": "flex justify-between items-center mb-8 mt-24"
                                },
                            ).get_text()
                            if price == "Prices May Vary":
                                price = "NA"
                            # Append list with name and price
                            kroger_data_list.append(
                                {
                                    # Add extra to the name to help be more specifc
                                    "name": name + " " + extra,
                                    # Split the original price from the current price
                                    "price": price.split(" ")[0],
                                }
                            )
                            if keyword[0].isnumeric() == True:
                                kroger_data_list.append({"upc": keyword})
                        # If itms are scraped terminate the for loop by success = True
                        success = True
        if success == False:
            kroger_data_list.append({"name": "Item unavailable at Kroger", "price": "NA"})
        
        return kroger_data_list

    ###########################################################################################################
    # Data analysis

    from collections import defaultdict
    import pandas as pd

    import sys


    def Dict2pandas(Store, name):
        """Change the tuple into a list of dictionaries before putting into pandas

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
    Wal = Dict2pandas(walmart(walmart_key), name[0])
    Ama = Dict2pandas(amazon(user_input), name[1])
    Krog = Dict2pandas(kroger(user_input), name[2])
    # Adjust the price and rating of each item into a float
    Krog["price"] = pd.to_numeric(Krog["price"], errors="coerce")
    Ama["Price"] = pd.to_numeric(Ama["Price"], errors="coerce")
    Ama["Rating"] = pd.to_numeric(Ama["Rating"], errors="coerce")

    # Create a list of the data frames to help combine them
    frames = [Wal, Ama, Krog]
    # Combined all three data frames
    df = pd.concat(frames)
    # Group them by the title name
    s = df.groupby(["Name", "Store Name"])["Price"].min()
    # print(s)

    ###########################################################################################################
    # Final GUI
    return show(df)

