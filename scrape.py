from requests_html import HTMLSession
import json
import sqlite3
from sqlite3 import Error
# import schedule
import time

# function to get values with a specific id from json


def get_img_ids(id, json_rep):
    result = []

    def break_dict(dictionary):
        try:
            result.append(dictionary[id])
        except KeyError:
            pass
        return dictionary
    json.loads(json_rep, object_hook=break_dict)
    return result


# function to get images urls from a list of images ids
def get_image_url(list):
    img_list = []
    for img in list:
        img_list.append(
            'https://img.hollisterco.com/is/image/anf/' + img + '?$product-medium-hol$')
    return img_list


# create connection for sqlite database
def create_connection(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error as e:
        print(e)
    return con


# create a table in database
def modify_table(con, table):
    try:
        c = con.cursor()
        c.execute(table)
    except Error as e:
        print(e)


# function to get all infomation, then insert them to girls_top and image_urls tables
def get_all_info(resource, connection, baseUrl):

    list = resource.html.find('li.product-card--hol')
    id = 1
    for item in list:
        name = item.find('a.product-card__name', first=True).text.strip()
        product_url = item.find('a.product-card__name',
                                first=True).attrs['href']
        if not product_url.startswith('http'):
            product_url = baseUrl + product_url

        price = item.find('.product-price-text.ds-override')
        original_price = price[0].text.strip()
        sale_price = ''
        if len(price) > 1:
            sale_price = price[1].text.strip()

        connection.execute('''INSERT INTO girls_top VALUES(?,?,?,?,?)''',
                           (id, name, product_url, original_price, sale_price))

        items = item.find(
            '.product-imageset', first=True).attrs['value']
        list_img = get_img_ids('id', items)
        list_img_urls = get_image_url(list_img)
        for img_url in list_img_urls:
            connection.execute('''INSERT INTO image_urls VALUES(?,?)''',
                               (id, img_url))
        connection.commit()
        id += 1


####################
def main():
    # set up requests_html
    baseUrl = 'https://www.hollisterco.com'
    session = HTMLSession(
        browser_args=["--no-sandbox", "--user-agent='Testing'"])
    url = 'https://www.hollisterco.com/shop/us/girls-tops'
    r = session.get(url)
    r.html.render(sleep=1)

    # set up tables
    database = "hollister.db"
    create_girls_top_table = '''CREATE TABLE girls_top (id INT PRIMARY KEY, name TEXT, product_url TEXT, original_price TEXT, sale_price TEXT);'''
    create_images_table = '''CREATE TABLE image_urls (item_id INT, image_url TEXT, PRIMARY KEY (item_id, image_url), FOREIGN KEY (item_id) REFERENCES girls_top (id));'''

    drop_girls_top_table = '''DROP TABLE girls_top'''
    drop_images_table = '''DROP TABLE image_urls'''

    con = create_connection(database)

    if con is not None:
        modify_table(con, drop_girls_top_table)
        modify_table(con, drop_images_table)
        modify_table(con, create_girls_top_table)
        modify_table(con, create_images_table)
    else:
        print("ERROR! Cannot create connection!")

    get_all_info(r, con, baseUrl)
    con.close()
###################


if __name__ == '__main__':
    main()

    # schedule.every(5).minutes.do(main)
    # while True:
    #     schedule.run_pending()

    # while True:
    #     main()
    #     time.sleep(5*60)
