import logging
import time
import requests
from typing import Any, Dict, List
import json

search_keyword = input("請輸入要搜尋的職缺關鍵字：")
# 設定日誌（Logging）基礎配置
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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
        # 直接呼叫內建方法將內容反序列化
        data: Dict[str, Any] = response.json()
        return data
        
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSON 格式解析失敗。HTTP 狀態碼: {response.status_code}")
        # 僅印出前 500 個字元作為除錯依據，避免佔用大量日誌空間
        logger.error(f"伺服器原始回傳內容 (部分): {response.text[:500]}")
        raise e

cookies = {
    '_ga': 'GA1.1.2030348356.1764120201',
    '_ga': 'GA1.4.2030348356.1764120201',
    'luauid': '2146175082',
    '_hjSessionUser_3218023': 'eyJpZCI6Ijc1ODE2MjY3LThlYzYtNWUzZS04MTk4LTcxZDY3MGQwZWU3MyIsImNyZWF0ZWQiOjE3NjQxMjAyMDE2MjksImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjMinimizedPolls': '1649289',
    'FOLLOW_JOB_PROMPT': '0',
    '_clck': 'yuqoyu%5E2%5Eg2v%5E0%5E2156',
    'ACUD': '9b677be5-2b63-462c-87ca-491cda1f841d',
    'LLM': 'identity',
    'job_same_ab': '1',
    'c_job_view_job_info_nabi': '8sbho%2C2008003003%2C2008003002%2C2007001020',
    'cf_clearance': 'mB6MPxCcuxwz9amoSrwULqn1y_bp50oPChKbJjbEHog-1772617166-1.2.1.1-kLMictM4olW5QEK1cw9KdEE86IySjElHWUOIfYBKyyukw1XJDIb4FCsPSw56BSKSHVyVdKddMWKE3TN3dTd3Y9_OnctrUrF2WFK6dtL3bcLHDpUYgJpcfB4OwaQqnrCeUmI_7ZQv78vhWzaCNuXfMTEXBk3l4MihtUFzAq1BDQl6uFcCrCuc2ScpILQewSrzzil.VxS9_4zbg4Q44OCjhqVJGtBygEdKlusjjQTgxiQ',
    '__cf_bm': 'Z78AvU1h5Aze5avFOQyAmG4JN8QnSYLhuCMjjK5cuqM-1773113029-1.0.1.1-ZvVxF02M_JDGzFNDRSFZR_06.JeymSsvg3Q5nIWy8LmwrkG07rmABtfCTvrtZqKUt037SMmMXdrI4eFL5DQD.gTeMujJ5oRif6UVEf3IVlc',
    '_cfuvid': '5t9yvre.T6hhNNgcjxJH.jgztAPX.T6uD46uN7yl7b8-1773113029160-0.0.1.1-604800000',
    '_hjSession_3218023': 'eyJpZCI6ImE5NWFkNDFkLWI2ZWMtNDY3MC04MzYyLWIyZGE3ODkzNTY4NCIsImMiOjE3NzMxMTMwMzIxODMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=',
    '_hjHasCachedUserAttributes': 'true',
    '_hp2_ses_props.3192618648': '%7B%22r%22%3A%22https%3A%2F%2Fwww.104.com.tw%2F%22%2C%22ts%22%3A1773113038490%2C%22d%22%3A%22signin.104.com.tw%22%2C%22h%22%3A%22%2F%22%7D',
    '_hp2_id.3192618648': '%7B%22userId%22%3A%227035907387929425%22%2C%22pageviewId%22%3A%223533035492830499%22%2C%22sessionId%22%3A%223312313741047499%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D',
    'AC': '1773113061',
    'EPK': '47cd24cd-d6e8-4802-9642-e316741bbb38',
    '_f': 'eyJpdiI6IlVCbXdoc2tpVEhtOWo4UjBrRjlDRlE9PSIsInZhbHVlIjoiejNleVg4STNKNHVoNC96V3RsZUtaWU1wOW8yTWhnSmt4S21ydm4zc2VPOE5XZmdCTzd5Q29rU0J0K2EyZFJJNE5SNWlJYVFERDI4MTdWWXgrUjJhWnc9PSIsIm1hYyI6ImVjOTliOGU2NmZiOTZlMzYxNWQ2YTcxOTcxZGM0NGY2NjdiZDY0N2EwNzY3MDNhNzAwYzBmNTY5ZmYyOTVjMDUiLCJ0YWciOiIifQ%3D%3D',
    'JBCLOGIN': 'vP0m3OeNBVNG34YvwJxJX5VWDMHX49G3Fz2rQggts9ysu',
    '_ga_TTXLT7SQ8E': 'GS2.1.s1773113038$o2$g1$t1773113065$j33$l0$h0',
    'c_white_bar_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2pvYi1ub3RpZnkuMTA0ZGMuY29tIiwic3ViIjoiJCQ6djE6TVowN1k4TWs3a0Z0ak1EYUFLd21rM0I3VGNVR1Nfdmh6TEl2MnpmMmQ3ejFVQlJ6a01oTGtnIiwiaWF0IjoxNzczMTEzMDY2LjQ3MDQ5NywiZXhwIjoxNzczMTE2NjY2LjQ3MDQ5N30.zJxHn7C3uVgM1f3ywR1wU0GepyNUGcSLz-wijp96YZI%2CeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJub3RpZmljYXRpb24uMTA0ZGMuY29tIiwiaWF0IjoxNzczMTEzMDY3LjA1ODQxMywiZXhwIjoxNzczMTE2NjY3LjA1ODQxMywicHJvZHVjdCI6ImpvYl9ub3RpZnlfc2VydmljZSIsImVuZHBvaW50IjoiY18wYjA3MTljOThmNjJjZDhmNzQ5NmEwY2Q4NzMxOTYzZSJ9.S25IjTg_1AzKBUAx9dvbUVrrEjejixXXFsanPU7lVW0',
    'c_white_bar_token_authentication': '95b15f8f9d52c8446fe833d0b34e82dc',
    'c_login_return_47cd24cd-d6e8-4802-9642-e316741bbb38_pc': '1',
    'c_white_bar_user_data': '%E5%B5%87%E5%A8%81%E5%A3%AC%2Cgiwalrian50902%40gmail.com',
    'personal-recommend-jobs-groups': '5',
    'c_white_bar_latest_match_time': '2026-03-10%2011%3A24%3A27',
    'cust_same_ab': '1',
    'bprofile_history': '%5B%2215741283000%22%2C%22130000000229061%22%2C%2253003028000%22%5D',
    '_gcl_au': '1.1.881971169.1772019135.1212824636.1773113078.1773113078',
    'lup': '2146175082.4507568175053.4623532291991.1.4640712161167',
    'lunp': '4623532291991',
    'c_job_search': '1',
    '_T_MYPOOL_104I': '4',
    'PROTOCOL104': 'http',
    '_ga_FJWMQR9J2K': 'GS2.1.s1773113031$o12$g1$t1773113358$j54$l0$h0',
    '_ga_WYQPBGBV8Z': 'GS2.4.s1773113031$o10$g1$t1773113358$j54$l0$h0',
    '_ga_W9X1GB1SVR': 'GS2.1.s1773113031$o12$g1$t1773113359$j53$l0$h0',
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
    'Connection': 'keep-alive',
    'Referer': 'https://www.104.com.tw/jobs/search/?area=6001001000,6001002000&jobexp=1&jobsource=joblist_search&keyword=%E8%BB%9F%E9%AB%94%E5%B7%A5%E7%A8%8B%E5%B8%AB&mode=s&order=15&page=1&searchJobs=1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': '_ga=GA1.1.2030348356.1764120201; _ga=GA1.4.2030348356.1764120201; luauid=2146175082; _hjSessionUser_3218023=eyJpZCI6Ijc1ODE2MjY3LThlYzYtNWUzZS04MTk4LTcxZDY3MGQwZWU3MyIsImNyZWF0ZWQiOjE3NjQxMjAyMDE2MjksImV4aXN0aW5nIjp0cnVlfQ==; _hjMinimizedPolls=1649289; FOLLOW_JOB_PROMPT=0; _clck=yuqoyu%5E2%5Eg2v%5E0%5E2156; ACUD=9b677be5-2b63-462c-87ca-491cda1f841d; LLM=identity; job_same_ab=1; c_job_view_job_info_nabi=8sbho%2C2008003003%2C2008003002%2C2007001020; cf_clearance=mB6MPxCcuxwz9amoSrwULqn1y_bp50oPChKbJjbEHog-1772617166-1.2.1.1-kLMictM4olW5QEK1cw9KdEE86IySjElHWUOIfYBKyyukw1XJDIb4FCsPSw56BSKSHVyVdKddMWKE3TN3dTd3Y9_OnctrUrF2WFK6dtL3bcLHDpUYgJpcfB4OwaQqnrCeUmI_7ZQv78vhWzaCNuXfMTEXBk3l4MihtUFzAq1BDQl6uFcCrCuc2ScpILQewSrzzil.VxS9_4zbg4Q44OCjhqVJGtBygEdKlusjjQTgxiQ; __cf_bm=Z78AvU1h5Aze5avFOQyAmG4JN8QnSYLhuCMjjK5cuqM-1773113029-1.0.1.1-ZvVxF02M_JDGzFNDRSFZR_06.JeymSsvg3Q5nIWy8LmwrkG07rmABtfCTvrtZqKUt037SMmMXdrI4eFL5DQD.gTeMujJ5oRif6UVEf3IVlc; _cfuvid=5t9yvre.T6hhNNgcjxJH.jgztAPX.T6uD46uN7yl7b8-1773113029160-0.0.1.1-604800000; _hjSession_3218023=eyJpZCI6ImE5NWFkNDFkLWI2ZWMtNDY3MC04MzYyLWIyZGE3ODkzNTY4NCIsImMiOjE3NzMxMTMwMzIxODMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MX0=; _hjHasCachedUserAttributes=true; _hp2_ses_props.3192618648=%7B%22r%22%3A%22https%3A%2F%2Fwww.104.com.tw%2F%22%2C%22ts%22%3A1773113038490%2C%22d%22%3A%22signin.104.com.tw%22%2C%22h%22%3A%22%2F%22%7D; _hp2_id.3192618648=%7B%22userId%22%3A%227035907387929425%22%2C%22pageviewId%22%3A%223533035492830499%22%2C%22sessionId%22%3A%223312313741047499%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; AC=1773113061; EPK=47cd24cd-d6e8-4802-9642-e316741bbb38; _f=eyJpdiI6IlVCbXdoc2tpVEhtOWo4UjBrRjlDRlE9PSIsInZhbHVlIjoiejNleVg4STNKNHVoNC96V3RsZUtaWU1wOW8yTWhnSmt4S21ydm4zc2VPOE5XZmdCTzd5Q29rU0J0K2EyZFJJNE5SNWlJYVFERDI4MTdWWXgrUjJhWnc9PSIsIm1hYyI6ImVjOTliOGU2NmZiOTZlMzYxNWQ2YTcxOTcxZGM0NGY2NjdiZDY0N2EwNzY3MDNhNzAwYzBmNTY5ZmYyOTVjMDUiLCJ0YWciOiIifQ%3D%3D; JBCLOGIN=vP0m3OeNBVNG34YvwJxJX5VWDMHX49G3Fz2rQggts9ysu; _ga_TTXLT7SQ8E=GS2.1.s1773113038$o2$g1$t1773113065$j33$l0$h0; c_white_bar_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2pvYi1ub3RpZnkuMTA0ZGMuY29tIiwic3ViIjoiJCQ6djE6TVowN1k4TWs3a0Z0ak1EYUFLd21rM0I3VGNVR1Nfdmh6TEl2MnpmMmQ3ejFVQlJ6a01oTGtnIiwiaWF0IjoxNzczMTEzMDY2LjQ3MDQ5NywiZXhwIjoxNzczMTE2NjY2LjQ3MDQ5N30.zJxHn7C3uVgM1f3ywR1wU0GepyNUGcSLz-wijp96YZI%2CeyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJub3RpZmljYXRpb24uMTA0ZGMuY29tIiwiaWF0IjoxNzczMTEzMDY3LjA1ODQxMywiZXhwIjoxNzczMTE2NjY3LjA1ODQxMywicHJvZHVjdCI6ImpvYl9ub3RpZnlfc2VydmljZSIsImVuZHBvaW50IjoiY18wYjA3MTljOThmNjJjZDhmNzQ5NmEwY2Q4NzMxOTYzZSJ9.S25IjTg_1AzKBUAx9dvbUVrrEjejixXXFsanPU7lVW0; c_white_bar_token_authentication=95b15f8f9d52c8446fe833d0b34e82dc; c_login_return_47cd24cd-d6e8-4802-9642-e316741bbb38_pc=1; c_white_bar_user_data=%E5%B5%87%E5%A8%81%E5%A3%AC%2Cgiwalrian50902%40gmail.com; personal-recommend-jobs-groups=5; c_white_bar_latest_match_time=2026-03-10%2011%3A24%3A27; cust_same_ab=1; bprofile_history=%5B%2215741283000%22%2C%22130000000229061%22%2C%2253003028000%22%5D; _gcl_au=1.1.881971169.1772019135.1212824636.1773113078.1773113078; lup=2146175082.4507568175053.4623532291991.1.4640712161167; lunp=4623532291991; c_job_search=1; _T_MYPOOL_104I=4; PROTOCOL104=http; _ga_FJWMQR9J2K=GS2.1.s1773113031$o12$g1$t1773113358$j54$l0$h0; _ga_WYQPBGBV8Z=GS2.4.s1773113031$o10$g1$t1773113358$j54$l0$h0; _ga_W9X1GB1SVR=GS2.1.s1773113031$o12$g1$t1773113359$j53$l0$h0',
}
page_current = 1
all_jobs_data : List[Dict[str,Any]] =[]

# 建立基礎的請求參數字典 (不包含動態的 page)
# 以下的參數為 104 搜尋職缺的 API 參數
# 臺北市、新北市
# 1年以下
# 搜尋軟體工程師
# 全職工作
base_params = {
    'area': '6001001000,6001002000',
    'jobexp': '1',
    'jobsource': 'joblist_search',
    'keyword': search_keyword,
    'mode': 's',
    'order': '15',
    'pagesize': '20',
    'ro': '1',
    'searchJobs': '1',
}
while True:
    # 動態更新當次請求的頁碼參數
    base_params['page'] = str(page_current)
    try:
        response = requests.get('https://www.104.com.tw/jobs/search/api/jobs', params=base_params, cookies=cookies, headers=headers)
        
        # 檢查 HTTP 狀態碼
        response.raise_for_status()

        # 呼叫上方定義好的解析函式來處理資料
        parsed_data: Dict[str, Any] = parse_api_response(response)

        # 解析 API 結構，處理 'data' 是 list 還是包裝在 dict 中的情況
        job_list = parsed_data.get('data')
        

        if not job_list:
            logger.info(f"第 {page_current} 頁沒有資料，資料收集完畢。")
            break

        # 將取得的資料併入總結果串列中
        all_jobs_data.extend(job_list)
        logger.info(f"成功取得第 {page_current} 頁，共 {len(job_list)} 筆職缺。")
        page_current += 1

        # 延遲以避免請求過於頻繁
        time.sleep(1.5)

    except requests.exceptions.RequestException as req_err:
        logger.error(f"網路請求發生異常: {req_err}")
        break  # 如果遇到網路錯誤則中斷
    except Exception as e:
        logger.exception(f"發生未預期的錯誤: {e}")
        break  # 防止無限迴圈

logger.info(f"爬蟲任務結束，總計取得 {len(all_jobs_data)} 筆職缺資料。")

Num = 1
# 1. 建立一個空的串列，用來收集所有清理好的特徵字典
final_extracted_list : List[Dict[str, Any]] =[]
def safe_get_and_strip(data_dict: Dict[str, Any], key: str, default: Any = None) -> Any:
    """安全提取字典欄位。
    
    若欄位值為字串，則執行 .strip() 去除前後空白 ; 若為其他型態則原樣回傳。
    加入型別檢查以防禦 `data_dict` 非字典型態造成的例外。
    
    Args:
        data_dict (Dict[str, Any]): 資料來源字典。
        key (str): 欲提取的鍵值名稱。
        default (Any, optional): 預設值。Defaults to None.
        
    Returns:
        Any: 經過清洗的欄位值。
    """
    # 防禦性編程：確保 data_dict 真的是屬字典型態，否則直接回傳預設值
    if not isinstance(data_dict, dict):
        return default

    value = data_dict.get(key, default)
    
    # 僅對字串型別進行 strip 操作
    if isinstance(value, str):
        return value.strip()
    return value

for job in all_jobs_data:

    # 提取關鍵特徵 (Feature Extraction)
    extract_features ={
        "編號": Num,
        "發布日期": safe_get_and_strip(job, "appearDate"),
        "職缺名稱" : safe_get_and_strip(job, "jobName"),
        "工作內容摘要" : safe_get_and_strip(job, "description"),
        "公司名稱" : safe_get_and_strip(job, "custName"),
        "產業描述" : safe_get_and_strip(job, "coIndustryDesc"),
        "最低薪資" : safe_get_and_strip(job, "salaryLow"),
        "最高薪資" : safe_get_and_strip(job, "salaryHigh"),
        "學歷要求代碼清單" : safe_get_and_strip(job, "optionEdu"),
        "具體的軟硬體技能要求" : safe_get_and_strip(job, "pcSkills"),
        "目前應徵人數" : safe_get_and_strip(job, "applyCnt"),
    }
    # 針對巢狀字典(Nested Dictionary)的安全提取
    link_dict = safe_get_and_strip(job, "link")
    extract_features["工作連結"] = safe_get_and_strip(link_dict, "job")
    
    # 將每一筆提取好的特徵字典加入至最終列表中 (補上原本遺漏的這行)
    final_extracted_list.append(extract_features)
    
    Num += 1

file_name = '2026AprilSoftwareEngineer.json'
with open(file_name, 'w', encoding='utf-8') as f:
    json.dump(final_extracted_list, f, ensure_ascii=False, indent=4)