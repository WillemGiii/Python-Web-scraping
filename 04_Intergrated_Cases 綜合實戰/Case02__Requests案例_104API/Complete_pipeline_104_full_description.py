"""104 職缺爬蟲：逐筆取得完整工作內容並輸出帶日期的資料檔。

1. 搜尋 API 只負責取得職缺清單。
2. 每筆職缺再呼叫詳情 API，取得完整的 ``jobDescription``。
3. 使用 Session、Retry 與請求間隔，降低暫時性錯誤與觸發限流的機率。
4. 輸出檔名包含執行日期，並統一存入同層的 ``dataset`` 資料夾。
"""

from __future__ import annotations

import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# 104 API 設定直接放在本檔案中，讓程式可以獨立執行。
API_URL = "https://www.104.com.tw/jobs/search/api/jobs"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.104.com.tw/jobs/search/",
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

# 注意：網站 Cookie 會過期。若日後出現 403，需要從瀏覽器更新這些值。
COOKIES = {
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


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SEARCH_REQUEST_DELAY = 1.5
DETAIL_REQUEST_DELAY = 1.5
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
SALARY_NEGOTIABLE_LOW = 40_000
SALARY_NEGOTIABLE_HIGH = 55_000


def create_session() -> requests.Session:
    """建立具有連線重用及暫時性錯誤重試功能的 HTTP Session。"""
    retry = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        status=MAX_RETRIES,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def safe_get(data: Any, key: str, default: Any = None) -> Any:
    """安全取得字典欄位；字串會移除頭尾空白。"""
    if not isinstance(data, dict):
        return default

    value = data.get(key, default)
    return value.strip() if isinstance(value, str) else value


def fetch_search_results(
    session: requests.Session,
    keyword: str,
) -> list[dict[str, Any]]:
    """逐頁取得搜尋結果；此處的 description 僅是搜尋摘要。"""
    jobs: list[dict[str, Any]] = []
    page = 1
    params = {
        "area": "6001001000,6001002000",
        "jobexp": "1",
        "jobsource": "joblist_search",
        "keyword": keyword,
        "mode": "s",
        "order": "15",
        "pagesize": "20",
        "ro": "1",
        "searchJobs": "1",
    }

    while True:
        params["page"] = str(page)
        response = session.get(API_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        page_jobs = response.json().get("data") or []
        if not page_jobs:
            break

        jobs.extend(page_jobs)
        logger.info("搜尋第 %s 頁：取得 %s 筆，累計 %s 筆", page, len(page_jobs), len(jobs))
        page += 1
        time.sleep(SEARCH_REQUEST_DELAY)

    return jobs


def fetch_full_description(
    session: requests.Session,
    job_url: str,
) -> str:
    """從職缺詳情 API 取得完整工作內容。"""
    job_id = job_url.rstrip("/").split("/")[-1]
    detail_url = f"https://www.104.com.tw/job/ajax/content/{job_id}"
    detail_headers = {"Referer": job_url}

    response = session.get(
        detail_url,
        headers=detail_headers,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    description = (
        response.json()
        .get("data", {})
        .get("jobDetail", {})
        .get("jobDescription", "")
    )
    return description.strip() if isinstance(description, str) else ""


def extract_jobs_with_full_description(
    session: requests.Session,
    search_jobs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """逐筆補上完整工作內容；詳情失敗時保留搜尋摘要並繼續執行。"""
    extracted_jobs: list[dict[str, Any]] = []
    total = len(search_jobs)

    for number, job in enumerate(search_jobs, start=1):
        link = safe_get(job, "link", {})
        job_url = safe_get(link, "job", "")
        description = ""

        if job_url:
            try:
                description = fetch_full_description(session, job_url)
            except (requests.RequestException, ValueError, KeyError) as error:
                logger.warning(
                    "[%s/%s] 詳情取得失敗，改用搜尋摘要：%s (%s)",
                    number,
                    total,
                    safe_get(job, "jobName", "未命名職缺"),
                    error,
                )

        if not description:
            description = safe_get(job, "description", "")

        extracted_jobs.append(
            {
                "編號": number,
                "發布日期": safe_get(job, "appearDate"),
                "職缺名稱": safe_get(job, "jobName"),
                "工作內容": description,
                "公司名稱": safe_get(job, "custName"),
                "產業描述": safe_get(job, "coIndustryDesc"),
                "最低薪資": safe_get(job, "salaryLow"),
                "最高薪資": safe_get(job, "salaryHigh"),
                "學歷要求代碼清單": safe_get(job, "optionEdu"),
                "具體的軟硬體技能要求": safe_get(job, "pcSkills"),
                "目前應徵人數": safe_get(job, "applyCnt"),
                "工作連結": job_url,
            }
        )

        logger.info("[%s/%s] 已處理：%s", number, total, safe_get(job, "jobName"))
        time.sleep(DETAIL_REQUEST_DELAY)

    return extracted_jobs


def degree_label(codes: Any) -> str:
    """將 104 學歷代碼清單轉換為易讀文字。"""
    if not isinstance(codes, list) or not codes:
        return "不拘"

    labels = {
        1: "國中",
        2: "高中",
        3: "專科",
        4: "大學",
        5: "碩士",
        6: "博士",
    }
    valid_codes = sorted(code for code in codes if code in labels)
    if not valid_codes:
        return "不拘"
    if len(valid_codes) == 1:
        return labels[valid_codes[0]]
    return f"{labels[valid_codes[0]]}以上"


def postprocess_jobs(jobs: list[dict[str, Any]]) -> pd.DataFrame:
    """篩選含 Python 的職缺，並處理面議薪資及學歷欄位。"""
    dataframe = pd.DataFrame(jobs)
    if dataframe.empty:
        return dataframe

    contains_python = dataframe["工作內容"].str.contains(
        "python",
        case=False,
        na=False,
    )
    dataframe = dataframe.loc[contains_python].copy()

    negotiable = (dataframe["最低薪資"] == 0) & (dataframe["最高薪資"] == 0)
    dataframe.loc[negotiable, "最低薪資"] = SALARY_NEGOTIABLE_LOW
    dataframe.loc[negotiable, "最高薪資"] = SALARY_NEGOTIABLE_HIGH
    dataframe["學歷要求代碼清單"] = dataframe["學歷要求代碼清單"].apply(degree_label)
    return dataframe


def filename_keyword(keyword: str) -> str:
    """將搜尋字詞轉換成適合 Windows 檔名的形式。"""
    normalized = re.sub(r"\s+", "_", keyword.strip())
    normalized = re.sub(r'[<>:"/\\|?*]', "_", normalized)
    return normalized or "jobs"


def save_results(
    all_jobs: list[dict[str, Any]],
    processed_jobs: pd.DataFrame,
    keyword: str,
    run_date: str,
) -> tuple[Path, Path, Path]:
    """將原始 JSON、處理後 JSON 與 CSV 存入 dataset。"""
    output_dir = Path(__file__).parent / "dataset"
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_keyword = filename_keyword(keyword)
    raw_path = output_dir / f"raw_jobs_{safe_keyword}_{run_date}.json"
    json_path = output_dir / f"processed_jobs_{safe_keyword}_{run_date}.json"
    csv_path = output_dir / f"processed_jobs_{safe_keyword}_{run_date}.csv"

    with raw_path.open("w", encoding="utf-8") as file:
        json.dump(all_jobs, file, ensure_ascii=False, indent=4)

    processed_jobs.to_json(json_path, orient="records", force_ascii=False, indent=4)
    processed_jobs.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return raw_path, json_path, csv_path


def main() -> None:
    """執行完整的搜尋、詳情擷取、後處理及輸出流程。"""
    started_at = datetime.now()
    started_counter = time.perf_counter()
    keyword = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else input(
        "請輸入職缺搜尋關鍵字："
    ).strip()

    if not keyword:
        raise ValueError("搜尋關鍵字不可為空白。")

    logger.info("程式開始時間：%s", started_at.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("搜尋關鍵字：%s", keyword)

    with create_session() as session:
        search_jobs = fetch_search_results(session, keyword)
        all_jobs = extract_jobs_with_full_description(session, search_jobs)

    processed_jobs = postprocess_jobs(all_jobs)
    output_paths = save_results(
        all_jobs=all_jobs,
        processed_jobs=processed_jobs,
        keyword=keyword,
        run_date=started_at.strftime("%Y%m%d"),
    )

    finished_at = datetime.now()
    elapsed_seconds = time.perf_counter() - started_counter
    logger.info("原始職缺：%s 筆；符合 Python 條件：%s 筆", len(all_jobs), len(processed_jobs))
    for output_path in output_paths:
        logger.info("已輸出：%s", output_path.resolve())
    logger.info("程式結束時間：%s", finished_at.strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("總執行時間：%.2f 秒", elapsed_seconds)


if __name__ == "__main__":
    main()
