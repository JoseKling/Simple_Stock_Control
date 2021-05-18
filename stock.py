#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 17 13:38:18 2021

@author: kling
"""

#%% Import packages

from Scanner.scanner import scanner
import sqlite3

#%% Define functions

def get_information(table, cursor):
    use_video = False
    #This is the device from which OpenCv will capture the video
    device = 'http://192.168.42.129:8080/video'
    if not use_video:
        check = False
    else:
        check, code = scanner(device)
    if not check:
        code = input('Please type the code of the product.\n')
        try:
            code = int(code)
        except:
            print("Not an integer. Please try again.")
            return(-1, -1)
    cursor.execute("SELECT COUNT(*) FROM {} WHERE Code = ?;"
                   .format(table), (code,))
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        print('No product found with this code.')
        return(code, 0)
    else:
        cursor.execute("SELECT * FROM {} WHERE Code = ?"
                       .format(table), (code,))
        info = cursor.fetchone()
        return(code, info)
    
def input_int(prompt, range_vals):
    incorrect = True
    while incorrect:
        choice = input(prompt)
        incorrect = False
        try:
            choice = int(choice)
        except:
            print('Must select an integer from {} to {}'
                  .format(range_vals[0], range_vals[1]))
            incorrect = True
        if not incorrect:
            if choice < range_vals[0] or choice > range_vals[1]:
                print('Must select an integer from {} to {}'
                  .format(range_vals[0], range_vals[1]))
                incorrect = True
    return(choice)

def update_table(table, field, value, code):
    try:
        cursor.execute("""
            UPDATE {}
            SET {} = ?
            WHERE Code = ?;
            """.format(table, field), (value, code))
    except:
        print("Invalid value. Try again.")
        
#%% Script

if __name__ == '__main__':
    
    #Initialize database
    database = 'Stock_Database.db'
    stock_table = 'Stock'
    price_table = 'Prices'
    
    connection = sqlite3.connect(database)
    
    cursor = connection.cursor()
    
    cursor.execute("""
           CREATE TABLE 
           IF NOT EXISTS {} (
           Code INT PRIMARY KEY,
           Product VARCHAR(30) NOT NULL,
           Retail_Price REAL NOT NULL,
           Purchase_Price REAL NOT NULL,
           Quantity INT NOT NULL,
           Low_Stock INT,
           High_Stock INT
           )
    """.format(stock_table))
    
    cursor.execute("""
           CREATE TABLE 
           IF NOT EXISTS {} (
           Code INT PRIMARY KEY,
           Product VARCHAR(30) NOT NULL,
           Price REAL NOT NULL
           )
    """.format(price_table))
    
    
    cont = True
    while cont:
        choice = input_int("""Select one of the options below:
    1 - Check product information.
    2 - Add product to stock.
    3 - Remove product from stock.
    4 - Check products too low in stock.
    5 - Check products too high in stock.
    6 - Remove product from stock list.
    7 - Change product information.
    8 - Close.
    """, (1,8))
        
        #Check product information
        if choice == 1:
            code, info = get_information(stock_table, cursor)
            if info != 0:
                print("""ID: {}
    Product: {}
    Retail Price: {:.2f}
    Purchase Price: {:2f}
    In stock: {}
    Low limit: {}
    High limit: {}
    """.format(*info))
    
        #Add product to stock
        elif choice == 2:
            code, info = get_information(stock_table, cursor)
            if info == 0:
                product = input('Please type the product name.\n')
                retail = input('Please type the product retail price.\n')
                purchase = input('Please type the product purchase price.\n')
                ammount = input('Please type the ammount of items to be added.\n')
                low_limit = input('Please type the low stock limit (or leave blank).\n')
                if low_limit == '':
                    low_limit = 0
                high_limit = input('Please type the high stock limit (or leave blank).\n')
                try:
                    cursor.execute("""
                        INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?);  
                    """.format(stock_table), 
                    (code, product, retail, purchase, ammount, low_limit, high_limit))
                    cursor.execute("""
                        INSERT INTO {} VALUES (?, ?, ?);  
                    """.format(price_table), (code, product, retail))
                except:
                    print('Could not add product. Check if all fields were typed correctly.')
            elif code > 1:
                print('This is the product name: {}'.format(info[1]))
                quantity = input('How many items should be added? ')
                try:
                    quantity = int(quantity)
                    prev = int(info[3])
                    new = prev + quantity
                    cursor.execute("""
                        UPDATE {}
                        SET Quantity = ?
                        WHERE Code = ?;
                    """.format(stock_table), (new, code))
                except:
                    print('The ammount of items must be an integer.')
            connection.commit()
         
        #Remove product from stock
        elif choice == 3:
            code, info = get_information(stock_table, cursor)
            if info == 0:
                print("Can't remove item because there is none in stock.\n")
            else:
                print('This is the current quantity in stock: {}'.format(info[3]))
                quantity = input('How many items should be removed? ')
                try:
                    quantity = int(quantity)
                    prev = int(info[3])
                    new = prev - quantity
                    if new < 0:
                        print("Can't remove more items than there are in stock.")
                    else:
                        cursor.execute("""
                            UPDATE Stock
                            SET Quantity = ?
                            WHERE Code = ?;
                        """, (new, code))
                except:
                    print('The ammount of items must be an integer.')
            connection.commit()
            
        #Check products below low limit
        elif choice == 4:
            cursor.execute("""
                SELECT Code, Product, Quantity, Low_Stock
                FROM {}
                WHERE Quantity <= Low_Stock;
            """.format(stock_table))
            print('Listing products below limit.')
            for row in cursor:
                print('Code: {}    Name: {}\nQuantity: {}    Limit: {}\n'
                      .format(*row))
     
        #Check products below high limit
        elif choice == 5:
            cursor.execute("""
                SELECT Code, Product, Quantity, High_Stock
                FROM {}
                WHERE Quantity >= High_Stock AND High_Stock != '';
            """.format(stock_table))
            print('Listing products above limit.')
            for row in cursor:
                print('Code: {}    Name: {}\nQuantity: {}    Limit: {}\n'
                      .format(*row))
        
        #Delete product entry from table
        elif choice == 6:
            code, info = get_information(stock_table, cursor)
            if info != 0:
                cursor.execute("""
                    DELETE FROM {}
                    WHERE Code = ?;
                """.format(stock_table), (code,))
                cursor.execute("""
                    DELETE FROM {}
                    WHERE Code = ?;
                """.format(price_table), (code,))
                
            print("Product deleted.")
            connection.commit()
        
        #Change product information
        elif choice == 7:
            code, info = get_information(stock_table, cursor)
            field = input_int("""Choose one option:
    1 - Change product name.
    2 - Change product retail price.
    3 - Change product purchase price.
    4 - Change product quantity.
    5 - Change low limit.
    6 - Change change high limit.
    """, (1,6))
            if info != 0 and info != -1:
                
                #Change product name
                if field == 1:
                    value = input("What is the new name?\n")
                    update_table(stock_table, 'Product', value, code)
                    update_table(price_table, 'Product', value, code)
                
                #Change product retail price
                if field == 2:
                    value = input("What is the new retail price?\n")
                    update_table(stock_table, 'Retail_Price', value, code)
                    update_table(price_table, 'Retail_Price', value, code)
                    
                #Change product purchase price
                if field == 3:
                    value = input("What is the new purchase price?\n")
                    update_table(stock_table, 'Purchase_Price', value, code)
                    update_table(price_table, 'Purcahse_Price', value, code)
                
                #Change product quantity
                if field == 4:
                    value = input("What is the new quantity?\n")
                    update_table(stock_table, 'Quantity', value, code)
                    
                #Change product low limit
                if field == 5:
                    value = input("What is the new low limit?\n")
                    update_table(stock_table, 'Low_Stock', value, code)
                    
                #Change product high limit
                if field == 6:
                    value = input("What is the new high limit?\n")
                    update_table(stock_table, 'High_Stock', value, code)
                    
                connection.commit()
        
        #Quit
        elif choice == 8:
            cont = False
            
        #Invalid choice
        else:
            print("Not a valid choice. Try again.")
     
    cursor.close()
    connection.close()