"""
104 人力銀行職缺爬蟲 — 完整 Pipeline
======================================
本模組整合以下三個獨立程式的功能：
    - module1_request_data.py   : 透過 104 API 爬取職缺資料並存成 JSON
    - module2_json2DataFrame.py : 將 JSON 資料轉換為 DataFrame / CSV
    - module3_Postprocessing.py : 篩選 Python 職缺、處理薪資面議、清洗學歷欄位並輸出結果

執行流程 (Pipeline):
    Step 1  爬蟲請求 (Crawling)
        → 向 104 API 分頁請求職缺資料
        → 將所有頁結果整理成 Python list，並序列化為 JSON 暫存檔

    Step 2  資料後處理 (Postprocessing)
        → 讀取 JSON，篩選含 "python" 關鍵字的職缺
        → 將薪資面議（值為 0 / 0）替換為估計值
        → 使用正規表達式將學歷代碼轉為中文標籤

    Step 3  資料匯出 (Export)
        → 輸出 JSON（供後續分析使用）
        → 輸出 CSV（供 Excel 開啟使用）

Note:
    原始三個獨立檔案（request_data.py、json2DataFrame.py、Postprocessing.py）
    保持不變，本檔案為整合版本，方便一次性執行完整作業流程。
"""

# ===========================================================================
# 標準函式庫
# ===========================================================================
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List

# ===========================================================================
# 日誌設定 (Logging Configuration)
# ===========================================================================
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ===========================================================================
# 第三方函式庫
# ===========================================================================
import pandas as pd
import requests

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except ImportError as e:
    logger.error("未偵測到 transformers 套件。請執行 'pip install transformers torch' 安裝必要依賴。")
    raise e

# ===========================================================================
# 常數設定 (Constants)
# ===========================================================================

# --- HTTP 請求標頭 ---
HEADERS: Dict[str, str] = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    "Referer": (
        "https://www.104.com.tw/jobs/search/"
        "?area=6001001000,6001002000&jobexp=1&jobsource=joblist_search"
        "&keyword=%E8%BB%9F%E9%AB%94%E5%B7%A5%E7%A8%8B%E5%B8%AB"
        "&mode=s&order=15&page=1&searchJobs=1"
    ),
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

# --- Cookie（來自瀏覽器，用於繞過反爬機制）---
COOKIES: Dict[str, str] = {
    "_ga": "GA1.4.2030348356.1764120201",
    "luauid": "2146175082",
    "_hjSessionUser_3218023": (
        "eyJpZCI6Ijc1ODE2MjY3LThlYzYtNWUzZS04MTk4LTcxZDY3MGQwZWU3MyIs"
        "ImNyZWF0ZWQiOjE3NjQxMjAyMDE2MjksImV4aXN0aW5nIjp0cnVlfQ=="
    ),
    "_hjMinimizedPolls": "1649289",
    "FOLLOW_JOB_PROMPT": "0",
    "_clck": "yuqoyu%5E2%5Eg2v%5E0%5E2156",
    "ACUD": "9b677be5-2b63-462c-87ca-491cda1f841d",
    "LLM": "identity",
    "job_same_ab": "1",
    "c_job_view_job_info_nabi": "8sbho%2C2008003003%2C2008003002%2C2007001020",
    "cf_clearance": (
        "mB6MPxCcuxwz9amoSrwULqn1y_bp50oPChKbJjbEHog-1772617166-1.2.1.1-"
        "kLMictM4olW5QEK1cw9KdEE86IySjElHWUOIfYBKyyukw1XJDIb4FCsPSw56BSK"
        "SHVyVdKddMWKE3TN3dTd3Y9_OnctrUrF2WFK6dtL3bcLHDpUYgJpcfB4OwaQqnr"
        "CeUmI_7ZQv78vhWzaCNuXfMTEXBk3l4MihtUFzAq1BDQl6uFcCrCuc2ScpILQew"
        "Srzzil.VxS9_4zbg4Q44OCjhqVJGtBygEdKlusjjQTgxiQ"
    ),
    "__cf_bm": (
        "Z78AvU1h5Aze5avFOQyAmG4JN8QnSYLhuCMjjK5cuqM-1773113029-1.0.1.1-"
        "ZvVxF02M_JDGzFNDRSFZR_06.JeymSsvg3Q5nIWy8LmwrkG07rmABtfCTvrtZqK"
        "Ut037SMmMXdrI4eFL5DQD.gTeMujJ5oRif6UVEf3IVlc"
    ),
    "_cfuvid": "5t9yvre.T6hhNNgcjxJH.jgztAPX.T6uD46uN7yl7b8-1773113029160-0.0.1.1-604800000",
    "_hjSession_3218023": (
        "eyJpZCI6ImE5NWFkNDFkLWI2ZWMtNDY3MC04MzYyLWIyZGE3ODkzNTY4NCIs"
        "ImMiOjE3NzMxMTMwMzIxODMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwi"
        "c2UiOjAsImZzIjowLCJzcCI6MX0="
    ),
    "_hjHasCachedUserAttributes": "true",
    "_hp2_ses_props.3192618648": (
        "%7B%22r%22%3A%22https%3A%2F%2Fwww.104.com.tw%2F%22%2C%22ts%22%3A"
        "1773113038490%2C%22d%22%3A%22signin.104.com.tw%22%2C%22h%22%3A"
        "%22%2F%22%7D"
    ),
    "_hp2_id.3192618648": (
        "%7B%22userId%22%3A%227035907387929425%22%2C%22pageviewId%22%3A"
        "%223533035492830499%22%2C%22sessionId%22%3A%223312313741047499"
        "%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D"
    ),
    "AC": "1773113061",
    "EPK": "47cd24cd-d6e8-4802-9642-e316741bbb38",
    "_f": (
        "eyJpdiI6IlVCbXdoc2tpVEhtOWo4UjBrRjlDRlE9PSIsInZhbHVlIjoiejNl"
        "eVg4STNKNHVoNC96V3RsZUtaWU1wOW8yTWhnSmt4S21ydm4zc2VPOE5XZmdC"
        "Tzd5Q29rU0J0K2EyZFJJNE5SNWlJYVFERDI4MTdWWXgrUjJhWnc9PSIsIm1h"
        "YyI6ImVjOTliOGU2NmZiOTZlMzYxNWQ2YTcxOTcxZGM0NGY2NjdiZDY0N2Ew"
        "NzY3MDNhNzAwYzBmNTY5ZmYyOTVjMDUiLCJ0YWciOiIifQ=="
    ),
    "JBCLOGIN": "vP0m3OeNBVNG34YvwJxJX5VWDMHX49G3Fz2rQggts9ysu",
    "_ga_TTXLT7SQ8E": "GS2.1.s1773113038$o2$g1$t1773113065$j33$l0$h0",
    "c_white_bar_token": (
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2pv"
        "Yi1ub3RpZnkuMTA0ZGMuY29tIiwic3ViIjoiJCQ6djE6TVowN1k4TWs3a0Z0"
        "ak1EYUFLd21rM0I3VGNVR1Nfdmh6TEl2MnpmMmQ3ejFVQlJ6a01oTGtnIiwi"
        "aWF0IjoxNzczMTEzMDY2LjQ3MDQ5NywiZXhwIjoxNzczMTE2NjY2LjQ3MDQ5"
        "N30.zJxHn7C3uVgM1f3ywR1wU0GepyNUGcSLz-wijp96YZI,"
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJub3RpZmljYXRp"
        "b24uMTA0ZGMuY29tIiwiaWF0IjoxNzczMTEzMDY3LjA1ODQxMywiZXhwIjox"
        "NzczMTE2NjY3LjA1ODQxMywicHJvZHVjdCI6ImpvYl9ub3RpZnlfc2Vydmlj"
        "ZSIsImVuZHBvaW50IjoiY18wYjA3MTljOThmNjJjZDhmNzQ5NmEwY2Q4NzMx"
        "OTYzZSJ9.S25IjTg_1AzKBUAx9dvbUVrrEjejixXXFsanPU7lVW0"
    ),
    "c_white_bar_token_authentication": "95b15f8f9d52c8446fe833d0b34e82dc",
    "c_login_return_47cd24cd-d6e8-4802-9642-e316741bbb38_pc": "1",
    "c_white_bar_user_data": "%E5%B5%87%E5%A8%81%E5%A3%AC%2Cgiwalrian50902%40gmail.com",
    "personal-recommend-jobs-groups": "5",
    "c_white_bar_latest_match_time": "2026-03-10%2011%3A24%3A27",
    "cust_same_ab": "1",
    "bprofile_history": "%5B%2215741283000%22%2C%22130000000229061%22%2C%2253003028000%22%5D",
    "_gcl_au": "1.1.881971169.1772019135.1212824636.1773113078.1773113078",
    "lup": "2146175082.4507568175053.4623532291991.1.4640712161167",
    "lunp": "4623532291991",
    "c_job_search": "1",
    "_T_MYPOOL_104I": "4",
    "PROTOCOL104": "http",
    "_ga_FJWMQR9J2K": "GS2.1.s1773113031$o12$g1$t1773113358$j54$l0$h0",
    "_ga_WYQPBGBV8Z": "GS2.4.s1773113031$o10$g1$t1773113358$j54$l0$h0",
    "_ga_W9X1GB1SVR": "GS2.1.s1773113031$o12$g1$t1773113359$j53$l0$h0",
}

# --- 薪資面議替代估計值 ---
SALARY_NEGOTIABLE_LOW: int = 40_000
SALARY_NEGOTIABLE_HIGH: int = 55_000

# --- API 端點 ---
API_URL: str = "https://www.104.com.tw/jobs/search/api/jobs"


def translate_chinese_to_english(text: str) -> str:
    """將中文文本翻譯為英文。

    使用 Hugging Face 的 AutoTokenizer 與 AutoModelForSeq2SeqLM
    載入 Helsinki-NLP/opus-mt-zh-en 模型以進行 Seq2Seq 機器翻譯。

    Args:
        text (str): 欲翻譯之中文文本。

    Returns:
        str: 翻譯完成之英文文本。

    Raises:
        Exception: 載入模型或進行翻譯推論失敗時拋出。
    """
    model_name: str = "Helsinki-NLP/opus-mt-zh-en"
    try:
        logger.info(f"開始載入機器翻譯模型：{model_name}...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        logger.info("模型載入成功，開始進行關鍵字翻譯...")
        inputs = tokenizer(text, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=50)
        translated_text: str = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"關鍵字翻譯完成。中文：'{text}' -> 英文：'{translated_text}'")
        return translated_text
    except Exception as e:
        logger.error(f"翻譯關鍵字時發生異常。詳細錯誤：{e}")
        raise e


# ===========================================================================
# Step 1：爬蟲請求 (Crawling)
# ===========================================================================

def parse_api_response(response: requests.Response) -> Dict[str, Any]:
    """解析來自 104 API 的 Response 物件並回傳為 Python 字典。

    此函式將進行 JSON 格式的反序列化，若伺服器回傳非 JSON 格式
    （例如被阻擋時出現的 HTML 頁面），則會記錄錯誤並拋出例外。

    Args:
        response (requests.Response): 由 requests 發送請求後取得的 HTTP 回應物件。

    Returns:
        Dict[str, Any]: 經解析後的 JSON 結構化字典資料。

    Raises:
        requests.exceptions.JSONDecodeError: 若回傳的內容無法成功解析為 JSON 時拋出。
    """
    try:
        data: Dict[str, Any] = response.json()
        return data
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSON 格式解析失敗。HTTP 狀態碼: {response.status_code}")
        logger.error(f"伺服器原始回傳內容 (部分): {response.text[:500]}")
        raise e


def safe_get_and_strip(data_dict: Dict[str, Any], key: str, default: Any = None) -> Any:
    """安全提取字典欄位。

    若欄位值為字串，則執行 .strip() 去除前後空白；
    若為其他型態則原樣回傳。加入型別檢查以防禦 `data_dict`
    非字典型態造成的例外。

    Args:
        data_dict (Dict[str, Any]): 資料來源字典。
        key (str): 欲提取的鍵值名稱。
        default (Any, optional): 預設值。Defaults to None.

    Returns:
        Any: 經過清洗的欄位值。
    """
    if not isinstance(data_dict, dict):
        return default

    value = data_dict.get(key, default)

    if isinstance(value, str):
        return value.strip()
    return value


def crawl_104_jobs(keyword: str, delay: float = 1.5) -> List[Dict[str, Any]]:
    """向 104 人力銀行 API 分頁爬取職缺，並回傳結構化特徵列表。

    本函式封裝整個爬蟲迴圈：從第 1 頁開始，持續請求直到
    API 不再回傳資料為止。每頁請求間隔 `delay` 秒以降低被封鎖的風險。

    Args:
        keyword (str): 要搜尋的職缺關鍵字（例如 "Python工程師"）。
        delay (float, optional): 每次分頁請求的間隔秒數。Defaults to 1.5.

    Returns:
        List[Dict[str, Any]]: 包含所有已提取特徵的職缺字典列表。

    Raises:
        requests.exceptions.RequestException: 發生網路層級錯誤時記錄並中止迴圈。
    """
    page_current: int = 1
    all_jobs_data: List[Dict[str, Any]] = []

    base_params: Dict[str, str] = {
        "area": "6001001000,6001002000",   # 臺北市、新北市
        "jobexp": "1",                      # 1 年以下
        "jobsource": "joblist_search",
        "keyword": keyword,
        "mode": "s",
        "order": "15",
        "pagesize": "20",
        "ro": "1",
        "searchJobs": "1",
    }

    while True:
        base_params["page"] = str(page_current)
        try:
            response = requests.get(
                API_URL,
                params=base_params,
                cookies=COOKIES,
                headers=HEADERS,
            )
            response.raise_for_status()

            parsed_data: Dict[str, Any] = parse_api_response(response)
            job_list = parsed_data.get("data")

            if not job_list:
                logger.info(f"第 {page_current} 頁沒有資料，資料收集完畢。")
                break

            all_jobs_data.extend(job_list)
            logger.info(f"成功取得第 {page_current} 頁，共 {len(job_list)} 筆職缺。")
            page_current += 1
            time.sleep(delay)

        except requests.exceptions.RequestException as req_err:
            logger.error(f"網路請求發生異常: {req_err}")
            break
        except Exception as e:
            logger.exception(f"發生未預期的錯誤: {e}")
            break

    logger.info(f"爬蟲任務結束，總計取得 {len(all_jobs_data)} 筆職缺資料。")

    # --- 特徵提取 (Feature Extraction) ---
    final_extracted_list: List[Dict[str, Any]] = []
    for num, job in enumerate(all_jobs_data, start=1):
        link_dict = safe_get_and_strip(job, "link")
        extract_features: Dict[str, Any] = {
            "編號": num,
            "發布日期": safe_get_and_strip(job, "appearDate"),
            "職缺名稱": safe_get_and_strip(job, "jobName"),
            "工作內容摘要": safe_get_and_strip(job, "description"),
            "公司名稱": safe_get_and_strip(job, "custName"),
            "產業描述": safe_get_and_strip(job, "coIndustryDesc"),
            "最低薪資": safe_get_and_strip(job, "salaryLow"),
            "最高薪資": safe_get_and_strip(job, "salaryHigh"),
            "學歷要求代碼清單": safe_get_and_strip(job, "optionEdu"),
            "具體的軟硬體技能要求": safe_get_and_strip(job, "pcSkills"),
            "目前應徵人數": safe_get_and_strip(job, "applyCnt"),
            "工作連結": safe_get_and_strip(link_dict, "job"),
        }
        final_extracted_list.append(extract_features)

    return final_extracted_list


def save_raw_json(data: List[Dict[str, Any]], output_path: Path) -> None:
    """將爬蟲原始結果序列化並儲存為 JSON 暫存檔。

    Args:
        data (List[Dict[str, Any]]): 爬蟲所得的職缺字典列表。
        output_path (Path): JSON 檔案的輸出路徑。

    Raises:
        IOError: 當檔案寫入失敗時拋出。
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"原始 JSON 已儲存至：{output_path.resolve()}")
    except Exception as e:
        raise IOError(f"JSON 寫入失敗：{e}")


# ===========================================================================
# Step 2：資料後處理 (Postprocessing)
# ===========================================================================

def filter_for_only_python(file_path: Path) -> pd.DataFrame:
    """讀取包含職缺資訊的 JSON 檔案，並篩選出「工作內容摘要」欄位中包含 "python" 的列。

    Args:
        file_path (Path): JSON 檔案的相對或絕對路徑。

    Returns:
        pd.DataFrame: 僅包含 'Python' 關鍵字的職缺資料表。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # 防禦性檢查：若 DataFrame 為空或沒有指定欄位，則回傳具有預期欄位的空 DataFrame
    if df.empty or "工作內容摘要" not in df.columns:
        logger.warning("資料來源為空或缺少 '工作內容摘要' 欄位，回傳空 DataFrame。")
        return pd.DataFrame(columns=[
            "編號", "發布日期", "職缺名稱", "工作內容摘要", "公司名稱",
            "產業描述", "最低薪資", "最高薪資", "學歷要求代碼清單",
            "具體的軟硬體技能要求", "目前應徵人數", "工作連結"
        ])

    # na=False：若該欄位為空值 (NaN)，不會引發錯誤而預設為 False
    condition = df["工作內容摘要"].str.lower().str.contains("python", na=False)
    return df[condition]


def fill_negotiable_salary(df_jobs: pd.DataFrame) -> pd.DataFrame:
    """將薪資面議（最低薪資與最高薪資皆為 0）的列替換為估計薪資值。

    Args:
        df_jobs (pd.DataFrame): 包含職缺資料的 DataFrame。

    Returns:
        pd.DataFrame: 薪資數值更新後的 DataFrame（副本）。
    """
    df_processed = df_jobs.copy()
    mask = (df_processed["最低薪資"] == 0) & (df_processed["最高薪資"] == 0)
    df_processed.loc[mask, "最低薪資"] = SALARY_NEGOTIABLE_LOW
    df_processed.loc[mask, "最高薪資"] = SALARY_NEGOTIABLE_HIGH
    return df_processed


def clean_degree_requirements_regex(df_degree: pd.DataFrame) -> pd.DataFrame:
    """使用正規表達式將 DataFrame 的「學歷要求代碼清單」欄位轉換為中文標籤。

    代碼對應規則：
        [1] → 國中, [2] → 高中, [3] → 專科, [4] → 大學, [5] → 碩士, [6] → 博士
        [1,...] → 學歷不拘, [2,...] → 高中以上, [3,...] → 專科以上,
        [4,...] → 大學以上, [5,...] → 碩士以上

    Args:
        df_degree (pd.DataFrame): 包含「學歷要求代碼清單」欄位的 DataFrame。

    Returns:
        pd.DataFrame: 更新「學歷要求代碼清單」標籤後的 DataFrame（副本）。
    """
    df = df_degree.copy()

    def match_degree_pattern(codes: Any) -> str:
        """將學歷代碼清單轉為對應中文標籤。

        Args:
            codes (Any): 學歷代碼的 list（例如 [4, 5]）。

        Returns:
            str: 對應的中文學歷標籤。
        """
        if not isinstance(codes, list) or not codes:
            return "未知"

        codes_str = "[" + ",".join(map(str, sorted(codes))) + "]"

        # 精確匹配：單一學歷
        if re.fullmatch(r"\[1\]", codes_str):
            return "國中"
        if re.fullmatch(r"\[2\]", codes_str):
            return "高中"
        if re.fullmatch(r"\[3\]", codes_str):
            return "專科"
        if re.fullmatch(r"\[4\]", codes_str):
            return "大學"
        if re.fullmatch(r"\[5\]", codes_str):
            return "碩士"
        if re.fullmatch(r"\[6\]", codes_str):
            return "博士"

        # 模糊匹配：多重學歷
        if re.match(r"\[1,.*\]", codes_str):
            return "學歷不拘"
        if re.match(r"\[2,.*\]", codes_str):
            return "高中以上"
        if re.match(r"\[3,.*\]", codes_str):
            return "專科以上"
        if re.match(r"\[4,.*\]", codes_str):
            return "大學以上"
        if re.match(r"\[5,.*\]", codes_str):
            return "碩士以上"

        return "未知"

    df["學歷要求代碼清單"] = df["學歷要求代碼清單"].apply(match_degree_pattern)
    return df


# ===========================================================================
# Step 3：資料匯出 (Export)
# ===========================================================================

def export_dataframe_to_json(df: pd.DataFrame, output_path: Path) -> None:
    """將 Pandas DataFrame 序列化並輸出為 JSON 檔案。

    採用 'records' 格式輸出，每一列資料會轉換為獨立的 JSON 物件。
    預設所有個資已完成脫敏處理（Data Anonymization）。

    Args:
        df (pd.DataFrame): 準備要轉換的 Pandas 資料表。
        output_path (Path): JSON 檔案的完整輸出路徑。

    Raises:
        ValueError: 當傳入的 DataFrame 為空時拋出。
        IOError: 當檔案寫入發生錯誤時拋出。
    """
    if df.empty:
        raise ValueError("傳入的 DataFrame 為空，無法進行 JSON 轉換作業。")

    try:
        df.to_json(
            path_or_buf=output_path,
            orient="records",
            force_ascii=False,
            indent=4,
        )
        logger.info(f"後處理 JSON 已匯出至：{output_path.resolve()}")
    except Exception as e:
        raise IOError(f"檔案寫入過程發生異常。詳細錯誤資訊：{e}")


def export_dataframe_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """將 Pandas DataFrame 匯出為 CSV 檔案（使用 utf-8-sig 確保 Excel 正常顯示）。

    Args:
        df (pd.DataFrame): 準備要轉換的 Pandas 資料表。
        output_path (Path): CSV 檔案的完整輸出路徑。

    Raises:
        ValueError: 當傳入的 DataFrame 為空時拋出。
        IOError: 當檔案寫入發生錯誤時拋出。
    """
    if df.empty:
        raise ValueError("傳入的 DataFrame 為空，無法進行 CSV 轉換作業。")

    try:
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"CSV 已匯出至：{output_path.resolve()}")
    except Exception as e:
        raise IOError(f"CSV 寫入過程發生異常。詳細錯誤資訊：{e}")


# ===========================================================================
# 主程式進入點 (Entry Point)
# ===========================================================================

if __name__ == "__main__":
    import sys
    # -----------------------------------------------------------------------
    # Step 0：關鍵字翻譯
    # -----------------------------------------------------------------------
    # 支援以命令列引數傳入關鍵字，避免 pipe 模式下的終端機編碼衝突
    if len(sys.argv) > 1:
        search_keyword: str = sys.argv[1]
    else:
        search_keyword = input("請輸入要搜尋的職缺關鍵字：")
        
    t_search_keyword: str = translate_chinese_to_english(search_keyword)
    safe_keyword: str = t_search_keyword.strip().replace(" ", "_")

    # -----------------------------------------------------------------------
    # Step 1：爬蟲請求
    # -----------------------------------------------------------------------
    extracted_jobs: List[Dict[str, Any]] = crawl_104_jobs(keyword=search_keyword)

    # 將爬蟲結果存為 JSON 暫存檔，檔名動態結合安全關鍵字
    base_dir: Path = Path(__file__).parent
    raw_json_path: Path = base_dir / f"raw_jobs_{safe_keyword}.json"
    save_raw_json(data=extracted_jobs, output_path=raw_json_path)

    # -----------------------------------------------------------------------
    # Step 2：資料後處理
    # -----------------------------------------------------------------------
    # 2-1. 篩選含 Python 關鍵字的職缺
    python_df: pd.DataFrame = filter_for_only_python(file_path=raw_json_path)

    # 2-2. 填補面議薪資
    python_df = fill_negotiable_salary(df_jobs=python_df)

    # 2-3. 清洗學歷欄位
    python_df = clean_degree_requirements_regex(df_degree=python_df)

    logger.info(f"後處理完成，共 {len(python_df)} 筆 Python 相關職缺。")

    # -----------------------------------------------------------------------
    # Step 3：資料匯出
    # -----------------------------------------------------------------------
    if python_df.empty:
        logger.warning("後處理完成，未找到任何符合 'python' 關鍵字的職缺。將跳過匯出 JSON 與 CSV 檔案之步驟。")
    else:
        # 3-1. 輸出後處理結果 JSON，檔名動態結合安全關鍵字
        processed_json_path: Path = base_dir / f"processed_jobs_{safe_keyword}.json"
        export_dataframe_to_json(df=python_df, output_path=processed_json_path)

        # 3-2. 輸出 CSV（供 Excel 開啟），檔名動態結合安全關鍵字
        csv_path: Path = base_dir / f"processed_jobs_{safe_keyword}.csv"
        export_dataframe_to_csv(df=python_df, output_path=csv_path)

    logger.info("Pipeline 全部完成。")
