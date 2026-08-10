import pandas as pd
import json
from pathlib import Path
import re

def Filter_for_only_Python(file_path: Path | str) -> pd.DataFrame:
    """
    讀取包含職缺資訊的 JSON 檔案，並篩選出「工作內容摘要」行(Column) 中 包含 "python'的列

    Parameters:
        file_path (str) : JSON 檔案的相對或絕對路徑
    
    Returns:
        pd.DataFrame : 僅包含 'Python'關鍵字的職缺資料表
    """
    # 讀取 JSON 檔案
    # 使用 json.load() 將文字解析為 Python 字典 / 列表格式
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 將 JSON 陣列轉換為 Pandas DataFrame
    df = pd.DataFrame(data)

    # 確認工作內容摘要所在的行 (Column) 包含 python
    # na=False 確保若該欄位為空值 (NaN)，不會引發錯誤而預設為 False
    con_desc = df['工作內容摘要'].str.lower().str.contains('python', na=False)

    # 篩選出包含 python 的工作
    python_jobs = df[con_desc]

    return python_jobs

def Salary_Negotiable(df_jobs: pd.DataFrame) -> pd.DataFrame:
    """
    讀取包含職缺的DataFrame，並尋找「面議」的薪資資料
    若["最低薪資"] 行 與 ["最高薪資"] 行 與該列的值皆為 0
    則將該列的["最低薪資"]修該為 40000，["最高薪資"]修該為 55000
    
    Parameters:
    df_jobs (pd.DataFrame) : 包含職缺資料的 DataFrame

    Returns:
    pd.DataFrame : 薪資數值更新後的 DataFrame

    """
    # 為了避免 SettingWithCopyWarning，建議先對傳入的資料表建立副本
    df_processed = df_jobs.copy()

    # 建立條件 : 最低薪資為 0 且 最高薪資為 0
    mask = (df_processed["最低薪資"] == 0) & (df_processed["最高薪資"] == 0)

    # 使用 .loc 將符合遮罩條件的列，其對應行的值替換為目標薪資
    df_processed.loc[mask, "最低薪資"] = 40000
    df_processed.loc[mask, "最高薪資"] = 55000

    return df_processed

def clean_degree_requirements_regex(df_Degree_mock: pd.DataFrame) -> pd.DataFrame:
    """
    使用正規表達式 (Regular Expression) 將 DataFrame 行內的學歷要求代碼清單進行轉換

    Parameters:
        df_Degree_mock (pd.DataFrame) : 包含「學歷要求代碼清單」行的 DataFrame

    Returns:
        pd.DataFrame : 更新 「學歷要求代碼清單」 標籤後的 DataFrame
    """

    # 建立副本以避免在原資料上產生副作用 (Side Effect)
    df = df_Degree_mock.copy()

    def match_degree_pattern(codes):
        # 防禦性程式設計 : 處理空值或非 list 型態
        if not isinstance(codes, list) or not codes:
            return "未知"
        
        # 確保代碼已由小到大排序，並轉換為緊湊字串格式 (無空白)
        # 例如 [5, 4] 會轉為 "[4,5]"
        codes_str = "[" + ",".join(map(str, sorted(codes))) + "]"

        # 1. 精確匹配：單一學歷的情況
        if re.fullmatch(r'\[1\]', codes_str): return '國中'
        if re.fullmatch(r'\[2\]', codes_str): return '高中'
        if re.fullmatch(r'\[3\]', codes_str): return '專科'
        if re.fullmatch(r'\[4\]', codes_str): return '大學'
        if re.fullmatch(r'\[5\]', codes_str): return '碩士'
        if re.fullmatch(r'\[6\]', codes_str): return '博士'
        
        # 2. 模糊匹配：多重學歷的情況 (即包含逗號的字串)
        if re.match(r'\[1,.*\]', codes_str): return '學歷不均'
        if re.match(r'\[2,.*\]', codes_str): return '高中以上'
        if re.match(r'\[3,.*\]', codes_str): return '專科以上'
        if re.match(r'\[4,.*\]', codes_str): return '大學以上'
        if re.match(r'\[5,.*\]', codes_str): return '碩士以上'
        
        return "未知"
    # 針對目標「 行(Column)」套用轉換邏輯
    df['學歷要求代碼清單'] = df['學歷要求代碼清單'].apply(match_degree_pattern)

    return df
    
def export_dataframe_to_json(df: pd.DataFrame, output_path: Path) -> None:
    """
    將 Pandas DataFrame 轉換並輸出為 JSON 檔案。

    處理過程中預設資料庫中的求職者個資或企業機敏資料已完成脫敏處理（Data Anonymization）。
    我們採用 'records' 格式來陣列化輸出，這會將每一筆資料列（Row）轉換成獨立的 JSON 物件。

    Args:
        df (pd.DataFrame): 準備要轉換的 Pandas 資料表（例如爬取整理後的 `python_jobs`）。
        output_path (Path): JSON 檔案的完整輸出路徑。

    Raises:
        ValueError: 當傳入的 DataFrame 為空，缺乏可輸出的資料時拋出異常。
        IOError: 當檔案寫入階段發生作業系統層級錯誤時拋出異常。
    """
    if df.empty:
        raise ValueError("傳入的 DataFrame 為空，無法進行 JSON 轉換作業。")

    try:
        # 執行 DataFrame 轉 JSON 的序列化與寫入作業
        # orient="records"：將表格轉為以列表包裝字典的形式（List of dictionaries）
        # force_ascii=False：確保繁體中文等非 ASCII 字元能正常寫入，不被轉為 Unicode 跳脫字元
        # indent=4：提供四格空白縮排，提升 JSON 檔案的肉眼可讀性
        df.to_json(
            path_or_buf=output_path,
            orient="records",
            force_ascii=False,
            indent=4
        )
        print(f"[系統日誌] 資料已成功匯出至：{output_path.resolve()}")
    except Exception as e:
        # 遵守嚴格報錯原則：禁止無聲壓制錯誤（Silent Error Suppression）
        raise IOError(f"檔案寫入過程發生異常。詳細錯誤資訊：{e}")

if __name__ == "__main__":
    
    # 1. 取得 JSON 檔案路徑
    file_path = input("請輸入 JSON 檔案的路徑：")

    filter_df = Filter_for_only_Python(file_path)

    df_salary_negotiable = Salary_Negotiable(filter_df)

    df_clean_degree_requirements = clean_degree_requirements_regex(df_salary_negotiable)

    python_jobs = pd.DataFrame(df_clean_degree_requirements)

    # 2. 定義輸出路徑：堅持使用 pathlib 以達到跨平台高兼容性
    # 這裡將檔案放置在當下執行的目錄下
    base_dir: Path = Path(__file__).parent
    target_json_path: Path = base_dir / "python_jobs.json"

    # 3. 呼叫函式執行 JSON 序列化
    export_dataframe_to_json(
        df=python_jobs, 
        output_path=target_json_path
    )