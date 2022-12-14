# PriceComparisonTool

Description: This program is a lightweight webscraper used to scan commonly used websites for a user-input item. 

Program Discription:
1. PyQt5 GUI window opens and prompts user for an item name to search the web for
PyQt5 assigns the user input as a string to a variable.
2. The variable is taken by beautiful soup, json, request, urlencode, and selector to scrape the web and return tuples of dictionaries.
3. An analysis portion of code loops through the collections dictionaries to refine the data into pandas database.
4. A pandasGUI GUI window opens to display the outputs.