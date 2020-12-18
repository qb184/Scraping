from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import json

baseUrl = 'https://www.hollisterco.com'
session = HTMLSession(browser_args=["--no-sandbox", "--user-agent='Testing'"])
url = 'https://www.hollisterco.com/shop/us/girls-tops'
r = session.get(url)
r.html.render(sleep=1)

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


# print(get_img_ids('id', items))

list = r.html.find('li.product-card--hol')

for item in list:
    name = item.find('a.product-card__name', first=True).text
    print(name)
    product_url = item.find('a.product-card__name', first=True).attrs['href']
    if not product_url.startswith('http'):
        product_url = baseUrl + product_url
    print(product_url)

    price = item.find('.product-price-text.ds-override')
    original_price = price[0].text
    print(original_price)
    sale_price = ''
    if len(price) > 1:
        sale_price = price[1].text
        print(sale_price)

    items = r.html.find('.product-imageset', first=True).attrs['value']
    list_img = get_img_ids('id', items)
    list_img_urls = get_image_url(list_img)
    print(list_img_urls)
