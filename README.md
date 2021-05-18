# Simple Stock Control
This is a stock control script implemented using SQLite.  
The Stock_Database.db contains two tables: Stock and Prices.

* Stock
	* Code - The barcode number of the product (int).
	* Product - The name of the product (varchar(30)).
	* Retail_Price - The sell price of the item (real).
	* Purchase_Price - The purchase price of the product (real).
	* Quantity - Ammount of items in stock (int).
	* Low_Stock - The lower limit for the ammount of items to be in stock (int).
	* High_Stock - The upper limit for the ammount of items to be in stock (int).
	
* Prices
	* Code - The barcode number of the product (int).
	* Product - The name of the product (varchar(30)).
	* Price - The sell price of the item (real).
	
There are also two scripts: stock.py and cashier.py.  
stock.py controls the Stock table, which, of course, affects the Prices table and is meant for personal in charge of stock control. cashier.py is used by the cashiers, as it only allows sells and checking item price and name.  
These separate tables are meant for security. In a better version there should be different permissions for each table (and, of course, permission for the database).  
In a future version a third table will be implemented, the Sells table, which will keep track of each sell with dates, the price of the sell and the profit. Also will be added a date field to the Stock table.

I used the code from the 'Barcode_Reader' repository to allow scanning bar codes of the products to add, modify or get items.
