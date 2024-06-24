import re
import requests
import time
import json

def extract_ids(link):
    product_id_pattern = r'\/([^\/]+)-p-(\d+)'
    merchant_id_pattern = r'merchantId=(\d+)'
    result = {
        "product_id_text": None,
        "product_id_number": None,
        "merchant_id": None,
        "product_code": None,
        "product_id": None
    }
    product_id_match = re.search(product_id_pattern, link)
    if product_id_match:
        result["product_id_text"] = product_id_match.group(1)
        result["product_id_number"] = product_id_match.group(2)
    merchant_id_match = re.search(merchant_id_pattern, link)
    if merchant_id_match:
        result["merchant_id"] = merchant_id_match.group(1)
    if result["product_id_text"] and result["product_id_number"]:
        result["product_code"] = f"{result['product_id_text']}-{result['product_id_number']}"
        result["product_id"] = f"{result['product_id_text']}-p-{result['product_id_number']}"
    return result

def fetch_product_reviews(merchant_id, product_id, max_pages=2):
    comments_list = []
    for rating in range(1, 6):
        for page_number in range(1, max_pages + 1):
            url = f"https://public-mdc.trendyol.com/discovery-web-websfxsocialreviewrating-santral/product-reviews-detailed?sellerId={merchant_id}&contentId={product_id}&page={page_number}&order=DESC&orderBy=Score&rates={rating}&channelId=1"
            try:
                response = requests.get(url)
                response.raise_for_status()
                content = response.json()
                comments = content["result"]["productReviews"]["content"]
                for comment in comments:
                    comments_list.append(comment["comment"])
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                continue
    return comments_list

def fetch_product_data(product_code, merchant_id):
    url = f'https://www.trendyol.com/comedones/{product_code}?boutiqueId=61&merchantId={merchant_id}&sav=true'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    text_data = response.text
    try:
        start_index = text_data.index("window.__PRODUCT_DETAIL_APP_INITIAL_STATE") + len("window.__PRODUCT_DETAIL_APP_INITIAL_STATE") + 3
        end_index = text_data.index("};", start_index) + 1
        json_string = text_data[start_index:end_index]
        data = json.loads(json_string)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing JSON data: {e}")
        return None
    descriptions = [description["text"] for description in data.get("product", {}).get("descriptions", [])]
    product_dataset = [
        f'{attribute["key"]["name"]} : {attribute["value"]["name"]}'
        for attribute in data.get("product", {}).get("attributes", [])
    ]
    return {
        "descriptions": descriptions,
        "product_dataset": product_dataset,
        "html_content": response.content,
        "text_data": text_data
    }

def scrapping_pipeline(link):
    ids = extract_ids(link)
    merchant_id, product_id, product_code = ids["merchant_id"], ids["product_id_number"], ids["product_id"]
    time.sleep(1)
    if not merchant_id:
        comments = fetch_product_reviews("0", product_id)
        time.sleep(1)
        product_details = fetch_product_data(product_code, "0")
        descriptions_text = " ".join(product_details["descriptions"])
        product_dataset_text = " ".join(product_details["product_dataset"])
    else:
        comments = fetch_product_reviews(merchant_id, product_id)
        time.sleep(1)
        product_details = fetch_product_data(product_code, merchant_id)
        descriptions_text = " ".join(product_details["descriptions"])
        product_dataset_text = " ".join(product_details["product_dataset"])
    return comments, descriptions_text, product_dataset_text

def question_tamplate(first_product_descriptions_text, first_product_data_text, second_product_descriptions_text, second_product_data_text):

    q_from_tempalate = f"""
    İlk ürünün bilgileri : {first_product_descriptions_text}
    ilk ürünün özellikleri : {first_product_data_text}
    ikinci ürünün bilgileri : {second_product_descriptions_text}
    ikinci ürünün özellikleri : {second_product_data_text}

    Sana iki ürün hakkında bilgi sağladım. Bu bilgileri kullanarak bu iki üründen hangisini alacağı konusunda kararsız kalan bir kullanıcının karar vermek için sorabileceği 10 soruyu bana ver.Cevabında sadece soruları sırala başka herhangi bir ek bilgi ya da açıklama yapma.
    """

    return q_from_tempalate

if __name__ == '__main__':
    product_info_map = {}
    product_links = [
        ["https://www.trendyol.com/xiaomi/redmi-watch-3-active-akilli-saat-p-744379766?boutiqueId=638145&merchantId=968", "https://www.trendyol.com/seyuwatch/watch-9-pro-akilli-saat-iphone-uyumlu-ve-android-tum-telefonlara-uyumlu-smartwatch-p-706351584?boutiqueId=61&merchantId=803260"],
        ["https://www.trendyol.com/teknoloji-gelsin/bluetooth-kulaklik-kulakici-powerbankli-cift-mikrofonlu-dokunmatik-kablosuz-earbuds-tws-p-218495477?boutiqueId=61&merchantId=117925", "https://www.trendyol.com/deilmi/dots-e6s-bluetooth-kulaklik-universal-hd-ses-ios-android-xiaomi-uyumlu-cift-mikrofon-extra-bass-ae6s-p-125042212?boutiqueId=61&merchantId=248749"],
        ["https://www.trendyol.com/watchofroyal/gunes-gozlugu-kadin-erkek-u v400-cam-ce-belgeli-rose-lorrainew-p-734165777", "https://www.trendyol.com/kinary/unisex-gunes-gozlugu-3-lu-firsat-seti-2028-p-784756196"],
        ["https://www.trendyol.com/philips/speedpro-max-sarjli-dikey-supurge-xc7043-1-elektrikli-25-2v-p-61607778", "https://www.trendyol.com/philips/speedpro-max-aqua-plus-kablosuz-dikey-supurge-aqua-baslik-led-baslik-xc8349-01-p-284597157"],
        ["https://www.trendyol.com/arzum/ar2062-g-airtasty-yagsiz-fitoz-airfryer-4-litre-kapasite-gumus-p-356159741", "https://www.trendyol.com/philips/3000-serisi-airfryer-0-8kg-4-1l-kapasite-siyah-hd9243-90-p-753537583"],
        ["https://www.trendyol.com/apple/iphone-11-64-gb-beyaz-cep-telefonu-aksesuarsiz-kutu-apple-turkiye-garantili-p-65149494", "https://www.trendyol.com/xiaomi/redmi-note-13-pro-12-gb-ram-512-gb-siyah-cep-telefonu-xiaomi-turkiye-garantili-p-797235137"],
        ["https://www.trendyol.com/xiaomi/mi-box-s-4k-android-tv-box-medya-oynatici-2-nesil-p-717630074", "https://www.trendyol.com/xiaomi/mi-tv-stick-4k-ultra-hd-dolby-chromecast-android-tv-media-player-p-301221564"],
        ["https://www.trendyol.com/comedones/dijital-baskul-yag-su-kas-vucut-kitle-endeksi-kilo-olcer-tarti-p-382995037", "https://www.trendyol.com/nivagatore/supscale-dijital-baskul-yag-su-kas-vucut-kitle-endeksi-kilo-olcer-tarti-p-84658219"],
        ["https://www.trendyol.com/kumtel/ko-40-tshdf-siyah-oval-set-ustu-cam-ocak-8mm-p-5608876", "https://www.trendyol.com/luxell/tshdf-siyah-dogalgazli-set-ustu-ankastre-cam-ocak-p-36353123"],
        ["https://www.trendyol.com/nacg/h2o-humidifier-400-ml-ulrasonik-hava-nemlendirici-buhar-makinesi-ve-aroma-difuzoru-h2o-4507-p-765602509?boutiqueId=61&merchantId=803985", "https://www.trendyol.com/heny/300-ml-hava-nemlendirici-buhar-makinasi-rgb-isikli-dekoratif-yanardag-p-805683046"],
        ["https://www.trendyol.com/xiaomi/s10-plus-beyaz-mop-robot-supurge-p-733153362?merchantId=968", "https://www.trendyol.com/roborock/q7-max-beyaz-akilli-robot-supurge-p-316610701?merchantId=106203"]
    ]


    for i, links in enumerate(product_links):
        link1, link2 = links[0], links[1]
        try:
            first_product_comments, first_product_descriptions_text, first_product_data_text = scrapping_pipeline(link1)
            second_product_comments, second_product_descriptions_text, second_product_data_text = scrapping_pipeline(link2)
        except Exception as e:
            print(f"Error scraping data for product pair {i}: {e}")
            continue
        product_info_map[str(i)] = {
            "first_product_comments": first_product_comments,
            "first_product_descriptions_text": first_product_descriptions_text,
            "first_product_data_text": first_product_data_text,
            "second_product_comments": second_product_comments,
            "second_product_descriptions_text": second_product_descriptions_text,
            "second_product_data_text": second_product_data_text,
            "template" : question_tamplate(first_product_descriptions_text, first_product_data_text, second_product_descriptions_text, second_product_data_text)
        }
        
    output_file_path = 'product_info_map.json'

    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(product_info_map, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {output_file_path}")