from bs4 import BeautifulSoup
import time
import csv
import requests
from typing import Union
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

import mysql.connector
from mysql.connector import Error
def connect_db():
    connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'))
     
    if connection.is_connected():
            print("Successfully connected to the database")
    return connection

def insert_data(values, connection):
    try:
    
    
            # Step 4: Create a Cursor Object
            cursor = connection.cursor()
            
            # Step 5: Create Table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS Product_Data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Title VARCHAR(255) NOT NULL,
                Price VARCHAR(255) NOT NULL,
                Image_Url VARCHAR(255) NOT NULL
            )
            """
            cursor.execute(create_table_query)
            print("Table 'Product_Data' created successfully")

            # Step 6: Write the SQL Insert Query
            sql_insert_query = """INSERT INTO Product_Data (Title, Price, Image_Url) 
                                  VALUES (%s, %s, %s)"""
            
            
            # Step 7: Execute the Insert Query
            cursor.executemany(sql_insert_query, values)
            
            # Step 8: Commit the Transaction
            connection.commit()
            print(f"{cursor.rowcount} Records inserted successfully into 'Product_Data' table")

    except Error as e:
        print(f"Error: {e}")
    
    finally:
        # Step 9: Close the Connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



@app.get("/scrap")
def scrap(url):
    response = requests.get(url)
    if "servis.pk" in url:

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup)
        title = soup.find("div", class_ = 'product__title')
        title_text=title.find("h1")
        print(title_text.text.strip())
        # print(price)
        discount_price = soup.find("span", class_ = 'price-item price-item--sale price-item--last')
        print(discount_price.text.strip())

        image = soup.find("div", class_ = 'product__media media media--transparent')
        picture = image.find('img')
        img_url= picture['src']

        full_image_url = f"https:{img_url}"

        print("Image URL:", full_image_url)
        return {'title':title_text.text.strip(), "price":discount_price.text.strip(), 'image':full_image_url }
    elif "bata.com.pk" in url:
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        # print(soup)
        title = soup.find("div", class_ = 'product__title')
        title_text=title.find("h1")
        print(title_text.text.strip())

        
        discount_price = soup.find("span", class_ = 'product_card_price')
        if discount_price is None:
            discount_price = soup.find("span", class_ = 'product_card_sale_price')
        
        print(discount_price.text.strip())
        image = soup.find("div", class_ = 'swiper-wrapper')
        print(image)
        picture = image.find('img')
        img_url= picture['src']
        full_image_url = f"https:{img_url}"

        print("Image URL:", full_image_url)
        values = [
                (title_text.text.strip(),discount_price.text.strip(),full_image_url)
            ]
        connection= connect_db()
        insert_data(values, connection)
        
        return {'title':title_text.text.strip(), "price":discount_price.text.strip(), 'image':full_image_url }
    else:
        return{"message":"This is not a servis or bata product"}
    
@app.get("/products")
def get_all_products():
    try:
        connection = connect_db()

        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # Use dictionary=True for fetching data as a dictionary
            cursor.execute("SELECT * FROM Product_Data")
            result = cursor.fetchall()

            if result:
                return {"products": result}
            else:
                return {"message": "No products found"}

    except Error as e:
        return {"error": str(e)}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")