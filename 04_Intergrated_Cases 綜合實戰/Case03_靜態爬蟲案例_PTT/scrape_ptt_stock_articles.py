# 若尚未安裝需要的套件，可在終端或 notebook 執行：
# !pip install requests beautifulsoup4 lxml

import requests
from bs4 import BeautifulSoup as bs
import lxml
import time
import json
import re
from datetime import datetime
from time import sleep
from typing import List, Dict, Optional


def get_current_month() -> int:
    """
    獲取當前月份
    
    Returns:
        int: 當前月份 (1-12)
    """
    current_time = datetime.now()
    return current_time.month


def get_last_month() -> int:
    """
    獲取上個月份
    
    Returns:
        int: 上個月份 (1-12)
    """
    current_month = get_current_month()
    return 12 if current_month == 1 else current_month - 1


def fetch_ptt_search_page(keyword: str, page: int = 1) -> bs:
    """
    抓取 PTT Stock 板的搜尋結果頁面
    
    Args:
        keyword: 搜尋關鍵字
        page: 頁碼，預設為 1
        
    Returns:
        BeautifulSoup: 解析後的 HTML 物件
        
    Raises:
        RuntimeError: 當 HTTP 請求失敗時
    """
    url = f'https://www.ptt.cc/bbs/Stock/search?page={page}&q={keyword}'
    res = requests.get(url)
    
    if res.status_code != 200:
        raise RuntimeError(f'取得網頁失敗，HTTP 狀態碼：{res.status_code}')
    
    return bs(res.text, 'lxml')


def filter_posts_by_month(soup: bs, target_month: int) -> List[str]:
    """
    篩選指定月份的文章，並回傳完整網址列表
    
    Args:
        soup: BeautifulSoup 物件
        target_month: 目標月份 (1-12)
        
    Returns:
        List[str]: 符合條件的文章完整網址列表
    """
    base_url = 'https://www.ptt.cc'
    target_urls = []
    pattern = f"{target_month}/"
    
    post_entries = soup.select('div.r-ent')
    print(f"找到 {len(post_entries)} 篇文章")
    
    for post in post_entries:
        date_tag = post.find(class_="date")
        if not date_tag:
            continue
            
        date_text = date_tag.text.strip()
        
        if date_text.startswith(pattern):
            a_tag = post.find('a')
            if a_tag and a_tag.get('href'):
                post_url = a_tag['href']
                complete_url = base_url + post_url
                target_urls.append(complete_url)
    
    return target_urls


def scrape_article_content(url: str) -> Optional[Dict]:
    """
    爬取單篇 PTT 文章的詳細內容
    
    Args:
        url: 文章完整網址
        
    Returns:
        Dict: 包含文章資訊的字典，若失敗則回傳 None
        字典包含: title, url, time, content, comments
    """
    try:
        res = requests.get(url)
        soup = bs(res.text, 'lxml')
        
        # 提取標題和時間
        meta_value = soup.select('span.article-meta-value')
        
        if len(meta_value) >= 3:
            title = meta_value[2].text
        else:
            title = "無標題或格式錯誤"
        
        if len(meta_value) >= 4:
            article_time = meta_value[3].text
        else:
            raise Exception("無時間或格式錯誤")
        
        # 提取留言
        comment_tags = soup.select('span.f3.push-content')
        comment_list = [c.text for c in comment_tags]
        
        # 提取內文
        main_content = soup.select_one('#main-content')
        
        if main_content:
            # 移除不需要的元素
            unwanted_elements = main_content.select(
                '.article-metaline, .article-metaline-right, span, div.push'
            )
            for element in unwanted_elements:
                element.decompose()
            
            content = main_content.text.strip()
            clean_content = content.replace('\n', ' ')
        else:
            clean_content = "無法提取內文"
        
        article_info = {
            "title": title,
            "url": url,
            "time": article_time,
            "content": clean_content,
            "comments": comment_list,
        }
        
        print(f"已成功爬取: {title}")
        return article_info
        
    except Exception as e:
        print(f"爬取失敗: {url}，錯誤原因: {e}")
        return None


def scrape_ptt_stock_articles(
    keyword: str,
    target_month: Optional[int] = None,
    page: int = 1,
    delay: float = 1.0,
    output_file: Optional[str] = None
) -> List[Dict]:
    """
    爬取 PTT Stock 板指定關鍵字和月份的文章
    
    Args:
        keyword: 搜尋關鍵字 (例如: "台達電")
        target_month: 目標月份，預設為上個月
        page: 搜尋頁碼，預設為 1
        delay: 每次請求間的延遲秒數，預設 1.0 秒
        output_file: 輸出 JSON 檔案路徑，若為 None 則不儲存
        
    Returns:
        List[Dict]: 文章資訊列表
    """
    # 設定目標月份
    if target_month is None:
        target_month = get_last_month()
    
    print(f"開始爬取關鍵字「{keyword}」在 {target_month} 月的文章...")
    
    # 步驟 1: 取得搜尋結果頁面
    soup = fetch_ptt_search_page(keyword, page)
    
    # 步驟 2: 篩選目標月份的文章網址
    target_urls = filter_posts_by_month(soup, target_month)
    print(f"找到 {len(target_urls)} 篇符合條件的文章")
    
    # 步驟 3: 逐一爬取文章內容
    articles_list = []
    for url in target_urls:
        article_info = scrape_article_content(url)
        if article_info:
            articles_list.append(article_info)
        sleep(delay)  # 避免被封鎖
    
    # 步驟 4: 儲存結果 (可選)
    if output_file:
        save_to_json(articles_list, output_file)
    
    print(f"爬取完成！共成功爬取 {len(articles_list)} 篇文章")
    return articles_list


def save_to_json(data: List[Dict], filename: str) -> None:
    """
    將資料儲存為 JSON 檔案
    
    Args:
        data: 要儲存的資料
        filename: 檔案名稱
    """
    output = json.dumps(data, ensure_ascii=False, indent=4)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"已儲存至 {filename}")


# ============ 使用範例 ============
if __name__ == "__main__":
    # 範例 1: 基本使用 - 爬取上個月的「台達電」文章
    articles = scrape_ptt_stock_articles(
        keyword="台達電",
        output_file="ptt_stock_articles.json"
    )
    
    # 範例 2: 自訂參數
    # articles = scrape_ptt_stock_articles(
    #     keyword="台積電",
    #     target_month=11,  # 指定 11 月
    #     page=1,
    #     delay=1.5,  # 延遲 1.5 秒
    #     output_file="tsmc_articles.json"
    # )
    
    # 範例 3: 不儲存檔案，只回傳資料
    # articles = scrape_ptt_stock_articles(keyword="鴻海")
    # print(f"共爬取 {len(articles)} 篇文章")
