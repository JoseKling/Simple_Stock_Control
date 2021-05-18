#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 14:11:42 2021

@author: kling
"""
#%% Import packages

import sqlite3
from stock import get_information, input_int
import numpy as np
import os.path

#%% Script

if __name__ == '__main__':
    database = 'Stock_Database.db'
    price_table = 'Prices'
    stock_table = 'Stock'
    
    if not os.path.isfile('./' + database):
        print("No database found. Exiting.")
        exit()
    
    connection = sqlite3.connect(database)
    
    cursor = connection.cursor()
    
    cont  = True
    while cont:
        
        choice = input_int("""Select one of the options below:
    1 - Start sale.
    2 - Check product information.
    3 - Quit
    """, (1,3))
    
        #Start sale
        if choice == 1:
            codes_list = []
            items_list = []
            quantity_list = []
            price_list = []
            code, info = get_information(price_table, cursor)
            if info != 0:
                try:
                    index = codes_list.index(code)
                    quantity_list[index] += 1
                except ValueError:
                    codes_list.append(code)
                    items_list.append(info[1])
                    quantity_list.append(1)
                    price_list.append(info[2])
            cont = False
            keep_going = True
        
        #Check product information
        elif choice == 2:
            code, info = get_information(price_table, cursor)
            if info != 0:
                print("""ID: {}
Product: {}
Price: {:.2f}
""".format(*info))  
            keep_going = True
        
        #Quit
        elif choice == 3:
            cont = False
            keep_going = False
            
        else:
            print("Not a valid choice. Try again.")
    #End of while
    
    while keep_going:
        action = input_int("""Choose an option.
0 - Checkout.
1 - Continue.
2 - Erase item from shop list.
3 - Get product information.
4 - Print shop list.
""",(0,4))

        #Checkout
        if action== 0:
            keep_going = False

        #Continue
        elif action == 1:
            code, info = get_information(price_table, cursor)
            if info != 0:
                try:
                    index = codes_list.index(info[0])
                    quantity_list[index] += 1
                except ValueError:
                    codes_list.append(info[0])
                    items_list.append(info[1])
                    quantity_list.append(1)
                    price_list.append(info[2])
        
        #Erase item from shop list
        elif action == 2:
            code, info = get_information(price_table, cursor)
            try:
                index = codes_list.index(info[0])
                codes_list.pop(index)
                items_list.pop(index)
                price_list.pop(index)
                quantity_list.pop(index)
            except ValueError:
                print("Could not find this product in the list.")
                
        #Check product information
        elif action == 3:
            code, info = get_information(price_table, cursor)
            if info != 0:
                print("""ID: {}
Product: {}
Price: {:.2f}
""".format(*info))

        #Print shop list
        elif action == 4:
            quantity_array = np.array(quantity_list)
            price_array = np.array(price_list)
            total_price = np.sum(quantity_array*price_array)
            for i in range(len(items_list)):
                print("Qt: {} - Price: {:.2f} - Product:{} - Total: {}"
                      .format(quantity_list[i], price_list[i], 
                              items_list[i], quantity_list[i]*price_list[i]))
            print("Total to pay: {:.2f}".format(total_price))
        
        #Invalid choice
        else:
            print("Not a valid choice. Try again.")       
    #End of while

    #Checking out. Print shop list and total and updates tables                
    quantity_array = np.array(quantity_list)
    price_array = np.array(price_list)
    total_price = np.sum(quantity_array*price_array)
    for i in range(len(items_list)):
        print("Qt: {} - Price: {:.2f} - Product:{} - Total: {}"
              .format(quantity_list[i], price_list[i], 
                      items_list[i], quantity_list[i]*price_list[i]))
    print("Total to pay: {0:.2f}".format(total_price))
    
    for i in range(len(codes_list)):
        cursor.execute("""
            SELECT Quantity
            FROM {}
            WHERE Code = ?;
        """.format(stock_table), (codes_list[i],))
        prev = cursor.fetchone()[0]
        new = prev - quantity_list[i]
        if new < 0:
            print("Product {} (Id {}) has negative ammount in stock. Check stock."
                  .format(items_list[i], codes_list[i]))
        cursor.execute("""
            UPDATE {}
            SET Quantity = ?
            WHERE code = ?;
        """.format(stock_table), (int(new), codes_list[i]))
    
    connection.commit()
    connection.close()