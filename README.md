# PriceComparisonTool

Description: This program is a lightweight webscraper used to scan commonly used websites for a user-input item. 

Program Discription:
1. PyQt5 GUI window opens and prompts user for an item name to search the web for
PyQt5 assigns the user input as a string to a variable.
2. The variable is taken by beautiful soup, json, request, urlencode, and selector to scrape the web and return tuples of dictionaries.
3. An analysis portion of code loops through the collections dictionaries to refine the data into pandas database.
4. A pandasGUI GUI window opens to display the outputs.

GUI Description: Once the user initiates the program, a small window named webscrapper will appear that asks for the item name or descriptor.
For the most accurate results type in the UPC code of the item. This is not necessary but helps the website narrow down the list of items being searched.
Once the user is done typing the item description, hit Run. This will prompt the webscrapping application. The webscrapper item box will stay open throughout 
the run. The item will then be searched through Walmart, Amazon and Krogers website. This process usually takes about 3 to 5 minutes to scrape the websites.
Once the item has been scraped at all three websites: Walmart, Target, and Amazon.

Know functional UPC codes:
	
	0001300000640


Output: 

The PandasGUI will open and display the list of items found in the webscrapping process. This GUI will 
contain the name of the item, the price, the star rating and the store name that it was found at. The PandasGUI will allow for easy data manipulation of the dataframe.


Price Comparison Tool Authors:

Carolyn Gerzina

Yash Patel

Kenneth West

University of Florida