"""
健行筆記軌跡數據爬蟲模組
=============================

本模組示範如何透過 ``requests`` 發送 AJAX 請求，並以 ``BeautifulSoup``
解析「健行筆記」(hiking.biji.co) 軌跡相關 GPX 紀錄頁面，
擷取各項運動指標（里程、耗時、爬升高度、下降高度、紀錄日期等）。

使用方式::

    python hiking_note_scraper.py
"""

import re
import pprint
from typing import Optional

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# 常數設定
# ---------------------------------------------------------------------------

BASE_URL: str = "https://hiking.biji.co/trail/ajax/load_related_gpx"

# 目標山岳與其在健行筆記對應的軌跡 ID
TRAIL_DATA: dict[str, int] = {
    "tao_mountain": 429,
    "tao_kalaye": 1746,
    "chiyou_pintian": 1737,
    "mt_beidawu": 1750,
    "mt_taguan": 1761,
    "mt_hijiayan": 531,
    "mt_junda": 500,
    "mt_xue_east": 1734,
    "mt_guanshangling": 1760,
    "hehuan_north": 288,
    "hehuan_north_west": 536,
    "mt_jade_front": 68,
}

# Cookies（從瀏覽器 DevTools 複製；具有時效性，過期後須重新取得）
COOKIES: dict[str, str] = {
    "_qg_fts": "1767931746",
    "QGUserId": "7370895265489497",
    "airisTracker": "PBVn1p7lgF8c",
    "_cc_id": "4e8b3cae7d543f4a9d88a12f901bff5c",
    "__htid": "ce1574f4-cb2e-4daf-bade-c85805e72fae",
    "AviviD_uuid": "a8427030-bdb8-4a6d-a4e0-ea6d251285f2",
    "webuserid": "074de9c8-faff-0f5b-702a-9f3fb714febf",
    "AviviD_refresh_uuid_status": "2",
    "cookieConsent": "true",
    "_ga_M7E3P87KRC": "GS2.1.s1768464677$o3$g0$t1768464677$j60$l0$h1043739287",
    "aiq_cs_5a937136420cfdf368a8": '[%22https:%22%2C%22biji.co%22%2C%22hiking%22%2C[[%22hiking%22%2C%22g%22]]]',
    "cto_bundle": "RedD_V82ZDl0M01BWmElMkZTMVolMkJsVFllaXFEbk5CbGh5T25rMjJ2NEppWTZHbkVmcWdMM1ZWTzZ6WmxyckVUV0p1UXJoZG1DcFJsbGh2SmZjMldwMXQ1OXpNaTZlSFRuJTJCOCUyQkY1eEltTGtpalBqaFFxdjZuWiUyRlFqV1RTZkN6QUZWRk1Wa2VVMWJyMkJPS01lMmY0dnprU2hKQUtRJTNEJTNE",
    "jiyakeji_uuid": "169f10e0-f6a7-11f0-a3f1-55d1c6e8be76",
    "_pubcid": "f71f7e42-b01e-45a2-a05d-6ebade1562b6",
    "_fbp": "fb.1.1782965731574.252662787824864391",
    "panoramaId_expiry": "1783570531614",
    "panoramaId": "a625a5ce4e2b30bf5f1e47ad705c16d53938f2907b2a6422fb89c4f21f88eee8",
    "panoramaIdType": "panoIndiv",
    "_gid": "GA1.2.1815987775.1782965732",
    "_qg_cm": "2",
    "_ht_hi": "1",
    "pacid": "pp.1.287506569.1780649264125",
    "AviviD_loadscript_log": "1",
    "_gcl_au": "1.1.1683444823.1782965734",
    "_ss_pp_id": "pp.1.660576542.1769047827201",
    "AviviD_already_exist": "1",
    "_ht_47b240": "1",
    "show_avivid_native_subscribe": "2",
    "_ht_f3244e": "1",
    "AviviD_session_id": "1782979270864",
    "_ga": "GA1.1.1068798473.1767931747",
    "FCCDCF": "%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22cbf7ea62-ac9c-4528-a944-f06e4960a97e%5C%22%2C%5B1767931746%2C578000000%5D%5D%22%5D%5D%5D",
    "cf_clearance": "HgQPR3VdBHrHNAtp6xecjoLmR6LF6mqdx6KmfAfYm1M-1782979273-1.2.1.1-Sb9JsC3PHkA1_HwJw1OiYvEuMeqNhoipUshb.TdKycNLwkHQ4qN5MTx2ojIONyCAhYyxKSBIFYIlYzAMb5oP1l51BkQdvK3OdhzlULBYLFYCAfQACVyrfYUp64GkxgamkjlqcwTtgGoizgUy3h3XpnpKpJ7UFBY68TfzD_SH6aQCNLwDZz0Cvuxq6PBgnH7KuP4dE5_bqPOFkrpsgrOdwPkABY5KyybtL8qugONHTvF21v0q4pEkYtxwmAAERAkQIkYd6RT3H979Lis6xf92V.zqWsqKPipk3aVax1aZI25dt2KpFdAR82NJ4K..O0rkXTI3V4hO_tMvnQuzCeIs8A",
    "_qg_pushrequest": "true",
    "FCNEC": "%5B%5B%22AKsRol8YwJY1R9ETGatn0cVv0bvdWZo4ymG8E4kW5AjoqXyKqZ4Qa95DkdhL1E4BzHXgYOtrgBIAjURoMKKwIKGQuyRk05XJ1RjhFig0_z2_1nVbo-3ijq2NEPaVXxx9rII4O6NHNUpSsD5vKoXELabxEqOODwLCCA%3D%3D%22%5D%5D",
    "_td": "7fc0fa11-e78e-4b6d-81a2-24ca84474bd6",
    "__eoi": "ID=b591f2634a33386f:T=1767931748:RT=1782979278:S=AA-AfjbTDG5cRq_LBETDLFXt9xdJ",
    "__gads": "ID=e8a48324d2edb2fd:T=1767931748:RT=1782979278:S=ALNI_MbfI3KSF1mjQtEovNOJXNPN3b609g",
    "__gpi": "UID=000011dfe7676648:T=1767931748:RT=1782979278:S=ALNI_MYM8VuVDx-kWA_8AR5i6JHF_UzK7g",
    "_ga_B7QHK7HLYB": "GS2.1.s1782979245$o5$g1$t1782979278$j27$l0$h0",
}

HEADERS: dict[str, str] = {
    "accept": "*/*",
    "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "priority": "u=1, i",
    "referer": "https://hiking.biji.co/index.php?q=trail&act=detail&id=288",
    "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    ),
}


# ---------------------------------------------------------------------------
# 工具函式
# ---------------------------------------------------------------------------


def parse_duration_to_minutes(duration_text: str) -> int:
    """將「X 小時 Y 分鐘」格式的字串轉換為總分鐘數。

    Args:
        duration_text: 原始耗時文字，例如 ``"2 小時 30 分鐘"`` 或 ``"45 分鐘"``。

    Returns:
        換算後的總分鐘數（整數）。若無法解析則回傳 ``0``。
    """
    hour_match = re.search(r"(\d+)\s*小時", duration_text)
    minute_match = re.search(r"(\d+)\s*分鐘", duration_text)

    hours: int = int(hour_match.group(1)) if hour_match else 0
    minutes: int = int(minute_match.group(1)) if minute_match else 0

    return hours * 60 + minutes


def parse_record(
    record_tag: "BeautifulSoup",
    trail_name: str,
) -> Optional[dict[str, object]]:
    """從單筆 ``<li>`` 標籤解析出軌跡紀錄資料。

    Args:
        record_tag: 代表一筆軌跡紀錄的 BeautifulSoup Tag 物件（``<li>``）。
        trail_name: 對應的山岳/路線名稱（英文識別碼）。

    Returns:
        包含以下欄位的字典：

        - ``trail_name`` (str): 路線識別碼
        - ``distance_km`` (str): 里程（公里）
        - ``duration_minutes`` (int): 耗時（分鐘）
        - ``ascent_m`` (str): 爬升高度（公尺）
        - ``descent_m`` (str): 下降高度（公尺）
        - ``record_date`` (str): 紀錄日期

        若解析失敗則回傳 ``None``。
    """
    # 里程（km）
    distance_text: str = record_tag.select("span")[0].text
    distance_match = re.search(r"([\d.]+)", distance_text)
    if not distance_match:
        return None
    distance_km: str = distance_match.group(1)

    # 耗時（分鐘）
    duration_text: str = record_tag.select("span.truncate")[0].text.strip()
    duration_minutes: int = parse_duration_to_minutes(duration_text)

    # 爬升高度（m）：移除千位分隔符後再解析
    ascent_text: str = record_tag.select("span")[2].text.replace(",", "").strip()
    ascent_match = re.search(r"(\d+)", ascent_text)
    if not ascent_match:
        return None
    ascent_m: str = ascent_match.group(1)

    # 下降高度（m）：移除千位分隔符後再解析
    descent_text: str = record_tag.select("span")[3].text.replace(",", "").strip()
    descent_match = re.search(r"(\d+)", descent_text)
    if not descent_match:
        return None
    descent_m: str = descent_match.group(1)

    # 紀錄日期
    record_date: str = record_tag.select("span")[4].text.strip()

    return {
        "trail_name": trail_name,
        "distance_km": distance_km,
        "duration_minutes": duration_minutes,
        "ascent_m": ascent_m,
        "descent_m": descent_m,
        "record_date": record_date,
    }


def fetch_page_records(
    hiking_note_id: int,
    page: int,
    trail_name: str,
) -> list[dict[str, object]]:
    """向健行筆記 AJAX 端點請求指定頁碼的軌跡紀錄，並解析回傳。

    Args:
        hiking_note_id: 健行筆記山岳/路線頁面的數字 ID。
        page: 欲抓取的分頁編號（從 1 開始）。
        trail_name: 對應的山岳/路線名稱（英文識別碼），用於標記資料來源。

    Returns:
        該頁所有有效紀錄的字典清單；若該頁無資料或請求失敗則回傳空清單。

    Raises:
        requests.HTTPError: 當 HTTP 回應狀態碼為 4xx / 5xx 時拋出。
    """
    params: dict[str, object] = {
        "id": hiking_note_id,
        "page": page,
        "device": "computer",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        cookies=COOKIES,
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    raw_html: str = response.json()["data"]["list"]

    # 健行筆記回傳的是 <li> 片段，需包在 <ul> 中才能正確解析
    soup = BeautifulSoup(f"<ul>{raw_html}</ul>", "lxml")
    li_tags = soup.ul.find_all("li", class_="flex", recursive=False)

    records: list[dict[str, object]] = []
    for li in li_tags:
        record = parse_record(li, trail_name)
        if record is not None:
            records.append(record)

    return records


def scrape_all_trails(
    trail_data: dict[str, int],
    max_pages: int = 9,
) -> list[dict[str, object]]:
    """爬取 ``trail_data`` 中所有路線的多頁軌跡紀錄。

    Args:
        trail_data: 路線識別碼（鍵）與健行筆記 ID（值）的對應字典。
        max_pages: 每條路線最多抓取的頁數（預設 9 頁）。

    Returns:
        所有路線、所有分頁的軌跡紀錄合併清單。
    """
    all_records: list[dict[str, object]] = []

    for trail_name, hiking_note_id in trail_data.items():
        print(f"\n{'=' * 50}")
        print(f"路線: {trail_name}（ID: {hiking_note_id}）")
        print("=" * 50)

        for page in range(1, max_pages + 1):
            page_records = fetch_page_records(hiking_note_id, page, trail_name)

            # 若該頁無資料，代表已到最後一頁，提前結束
            if not page_records:
                print(f"  第 {page} 頁無資料，停止翻頁。")
                break

            print(f"  第 {page} 頁：取得 {len(page_records)} 筆紀錄")
            pprint.pprint(page_records)
            all_records.extend(page_records)

    return all_records


# ---------------------------------------------------------------------------
# 主程式入口
# ---------------------------------------------------------------------------


def main() -> None:
    """主執行函式：爬取健行筆記各路線軌跡資料並印出結果。"""
    all_records = scrape_all_trails(TRAIL_DATA, max_pages=9)

    print(f"\n{'=' * 50}")
    print(f"總計取得 {len(all_records)} 筆軌跡紀錄")
    print("=" * 50)


if __name__ == "__main__":
    main()
