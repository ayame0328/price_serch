from bs4 import BeautifulSoup
import urllib.request
import re
import requests
import datetime

# 商品リンクのリストを取得する関数
def get_product_links(base_url):
    """
    指定された価格.comのランキングページから商品のリンクリストを取得します。

    Args:
    base_url (str): ランキングページのURL。

    Returns:
    list: 商品ページのURLリスト。
    """
    page_count = 1
    linklist = []
    while True:
        category_res = requests.get(base_url + "?page=" + str(page_count)).text
        soup = BeautifulSoup(category_res, 'html.parser')
        for elm in soup.find_all("a"):
            if 'href' in elm.attrs:
                link_url = elm.attrs['href']
                if "https://kakaku.com/item/" in link_url:
                    linklist.append(link_url)
        a_next_tag= soup.find_all("li", {"class": "next"})
        if a_next_tag:
            page_count += 1
            continue
        break
    return sorted(list(set(linklist)), key=linklist.index)

# CSVヘッダーを書き込む関数
def write_csv_header(filename):
    """
    CSVファイルのヘッダーを書き込みます。

    Args:
    filename (str): CSVファイルの名前。

    Returns:
    None
    """
    with open(filename, 'a', encoding='cp932', errors='ignore') as f:
        f.write("タイトル名,最低価格,クレジット最低価格,価格URL,\n")

# 商品情報をCSVファイルに書き込む関数
def write_product_info_to_csv(linklist, filename):
    """
    商品ページから商品情報を取得し、それをCSVファイルに書き込みます。

    Args:
    linklist (list): 商品ページのURLリスト。
    filename (str): CSVファイルの名前。

    Returns:
    None
    """
    for page_url in linklist:
        page_html = page_url + "spec/#tab"
        res = urllib.request.urlopen(page_html)
        page_soup = BeautifulSoup(res, 'html.parser')
        name = page_soup.find("h2", itemprop="name").text
        low_price = get_price(page_soup, "div", "priceWrap")
        cre_price = get_price(page_soup, "div", "creditCard")
        with open(filename, 'a', encoding='cp932', errors='ignore') as f:
            f.write(f"{name},{low_price},{cre_price},{page_url},\n")

# 価格情報を取得する関数
def get_price(soup, tag, class_name):
    """
    指定されたタグとクラス名から価格情報を抽出します。

    Args:
    soup (bs4.BeautifulSoup): BeautifulSoupオブジェクト。
    tag (str): 検索するHTMLタグ。
    class_name (str): 検索するHTMLタグのクラス名。

    Returns:
    str: 抽出された価格情報。
    """
    try:
        price = soup.find(tag, class_=class_name).find("span", class_="priceTxt").text
        return price.replace(',', '')
    except AttributeError:
        return ''

# メイン処理
def main():
    url = input("人気売れ筋ランキングのページURLを入力してください。:")
    links = get_product_links(url)
    now = datetime.datetime.now()
    filename = "switch_game" + now.strftime('%Y%m%d_%H%M%S') + '.csv'
    write_csv_header(filename)
    write_product_info_to_csv(links, filename)


