from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import os
import csv
import time

# 入力CSVファイル名をユーザに入力してもらう
input_csv_file = input("元のCSVファイル名を入力してください（拡張子含む）: ")

# 日付をファイル名から抽出
date_str = input_csv_file.split('switch_game')[1].split('_')[0]

# 日付フォルダのパスを設定（例：20230415）
date_folder_path = os.path.join(os.getcwd(), date_str)

# 日付フォルダが存在しない場合は作成
if not os.path.exists(date_folder_path):
    os.makedirs(date_folder_path)

# prevフォルダのパスを設定
prev_folder_path = os.path.join(date_folder_path, 'prev')

# prevフォルダが存在しない場合は作成
if not os.path.exists(prev_folder_path):
    os.makedirs(prev_folder_path)

# Selenium WebDriverを起動（Edge）
driver = webdriver.Edge()

# 入力CSVファイルを読み込む
with open(input_csv_file, 'r', newline='', encoding='cp932') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        # 商品名とURLを取得
        product_name = row['タイトル名'].replace('/', '-')
        url = row['価格URL']
        
        # 出力CSVファイル名を設定（例：prev/商品名.csv）
        csv_file_name = os.path.join(prev_folder_path, product_name + ".csv")
        
        # URLを開く
        driver.get(url)
        
        # レビューボタンを見つけてクリックする
        try:
            review_button = driver.find_element(By.XPATH, '//*[@id="ovBtnBox"]/ul/li[2]/a')
            review_button.click()
            # 少し待ってページが完全にロードされるのを確実にする
            time.sleep(5)
             # 現在のURLを確認
            current_url = driver.current_url
            if "https://ssl.kakaku.com/auth/id/login/" in current_url:
                # ログインページにリダイレクトされた場合は、処理をスキップして次の行に進む
                print(f"{product_name} - ログインページにリダイレクトされたため、スキップします。")
                continue
        except NoSuchElementException:
            # レビューボタンが見つからない場合は、処理をスキップして次の行に進む
            print(f"{product_name} - レビューボタンが見つからないため、スキップします。")
            continue
        
        # 評価項目のテーブルを取得
        table_rows = driver.find_elements(By.XPATH,'//*[@id="revbox"]/div[2]/div/table/tbody/tr')
        
        # CSVファイルに書き込み
        with open(csv_file_name, 'w', newline='', encoding='cp932') as output_file:
            writer = csv.writer(output_file)
            # テーブルのヘッダーを書き込み
            writer.writerow(['評価項目', '投票平均', 'カテゴリ平均', '項目別ランキング'])
            
            # テーブルの行をループしてデータを書き込む
            for row in table_rows[1:]:  # ヘッダー行をスキップするために[1:]を使用
                cells = row.find_elements(By.TAG_NAME, 'td')
                if cells and len(cells) >= 4:  # 4つ以上のセルがあることを確認
                    rev_head = cells[0].text.strip()
                    rating = cells[1].find_element(By.TAG_NAME, 'span').get_attribute('textContent').strip()
                    average = cells[2].text.strip()
                    rank = cells[3].text.strip().replace('位', '')  # '位' 文字を削除
                    writer.writerow([rev_head, rating, average, rank])
        
        print(f"{product_name}の情報を{csv_file_name}に書き込みました。")

# WebDriverを閉じる
driver.quit()
