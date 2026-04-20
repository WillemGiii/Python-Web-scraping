import json
from pathlib import Path
import shutil

# 定義路徑
base_dir = Path(r"c:\Users\mapd\OneDrive - ispan.com.tw\桌面\2_教學研發\02_Python_Web_Scraping\2_Code_Examples\01_Module_Requests")
original_file = base_dir / "01_Get_Request.ipynb"
teacher_file = base_dir / "01_Get_Request_Teacher.ipynb"

# 1. 備份原版為教師版 (保留完整解答與原始輸出結果)
if not teacher_file.exists():
    shutil.copy(original_file, teacher_file)
    print(f"已建立教師版備份：{teacher_file.name}")

# 2. 讀取並修改內容以產生學生練習版
with open(original_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        # 清除輸出結果與執行次數，讓學生的版面保持整潔
        cell["outputs"] = []
        cell["execution_count"] = None
        
        source = "".join(cell.get("source", []))
        
        # 進行關鍵字替換，依照不同段落轉為挖空版的半完成品
        if "res = requests.get('https://httpbin.org/get')" in source and "status_code" in source:
            source = """import requests\n\n# 1. 對目標網址發送 GET 請求，並將完整的伺服器回應存入 'res' 變數中\nres = None  # TODO: 使用 requests 發送 GET 請求到 'https://httpbin.org/get'\n\n# 我們一起觀察這個物件有甚麼屬性和功能\n\n# 2. 檢查回應狀態碼，200 代表請求成功\n# 狀態碼可以告知我們請求的處理狀態\nprint(f"Status Code: {None}")  # TODO: 輸出狀態碼 (status_code)\n\n# 3. 查看 requests 函式庫自動判斷的編碼格式\nprint(f"Encoding: {None}")  # TODO: 輸出編碼格式 (encoding)\n\n# 4. 輸出解碼後的文字內容\nprint("\\n--- Response Text ---")\n# TODO: 印出回應的純文字內容 (text)\n"""
        elif "my_params =" in source and "'key1': 'value1'" in source:
            source = """# 1. 定義一個字典來存放要附加到 URL 的查詢參數 (Query String)\n#    requests 函式庫會自動將其轉換為 "?key1=value1&key2=value2" 的格式\nmy_params = {\n    # TODO: 建立 key1: value1, key2: value2 的鍵值對\n}\n\n# 2. 在 GET 請求中，透過 params 參數傳遞我們的字典\nres = None  # TODO: 發送包含 params 參數的 GET 請求\n\n# 3. 透過 res.url 屬性觀察 requests 實際發出的完整 URL\nprint(f"Final URL: {None}")  # TODO: 輸出最終發出的 URL\n\n# 4. 輸出伺服器回應的內容，確認參數已被伺服器接收\nprint("\\n--- Response Text ---")\n# TODO: 印出回應的純文字內容 (text)\n"""
        elif "my_headers =" in source and "user-agent" in source:
            source = """# 1. 定義一個字典來存放自訂的請求標頭 (Request Headers)\n#    'user-agent' 最常被用來告訴伺服器我們是什麼樣的瀏覽器。\nmy_headers = {\n    # TODO: 加入 user-agent 標頭（可隨意偽造一個常見的瀏覽器字串）\n}\n\n# 2. 在 GET 請求中，透過 headers 參數傳遞自訂標頭字典\nres = None  # TODO: 發送包含 headers 的 GET 請求\n\n# 3. 輸出伺服器回應內容，觀察 User-Agent 欄位是否改變\nprint("--- Response Text ---")\n# TODO: 印出回應的純文字內容 (text)\n"""
        elif "my_cookies =" in source and "first_cookie" in source:
            source = """# 1. 定義一個字典來存放要傳送的 Cookie\nmy_cookies = {\n    # TODO: 加入兩組 Cookie，例如 "first_cookie": "hello"\n}\n\n# 2. 在 GET 請求中，透過 cookies 參數傳遞自訂 Cookie 字典\nres = None  # TODO: 發送包含 cookies 的 GET 請求\n\n# 3. 輸出伺服器回應內容，觀察 Cookie 欄位是否成功帶上\nprint("--- Response Text ---")\n# TODO: 印出回應的純文字內容 (text)\n"""
        elif "url = 'https://csm.api.opentix.life/programs" in source and "program_list =" in source:
            source = """import requests\nimport json\n\n# 1. 定義要請求的 API 網址\nurl = 'https://csm.api.opentix.life/programs?page=44&rowCount=10'\n\n# 2. 發送 GET 請求\nres = None  # TODO: 發送 GET 請求\n\n# 3. 觀察伺服器回傳的原始內容\nprint("--- Raw Response Text (type: str) ---")\n# print(res.text[:300] + "...") \n\n# 4. 將 JSON 格式的字串轉換為 Python 物件 (字典)\nobj = None  # TODO: 取得 JSON 物件 (提示: 可使用 res.json() 或 json.loads())\n\n# 5. 解析並提取資料\nprint("--- Accessing Nested Data ---")\n# TODO: 嘗試用 print 取出 obj['result'] 來觀察結構\n\n# 6. 遍歷資料列表\nprogram_list = []  # TODO: 從 obj 中提取存放節目的列表 (提示: 觀察 data 階層)\nprint("\\n--- Iterating Through Program List ---")\nfor program in program_list:\n    pass # TODO: 印出每一個節目的名稱 (name) 與 類別 (displayCategory)\n"""
        elif "import pprint" in source:
            source = """import requests\nimport json\nimport pprint\n\nurl = 'https://csm.api.opentix.life/programs?page=1&rowCount=10'\nres = None # TODO: 發送 GET 請求\nobj = None # TODO: 解析為 JSON\n# TODO: 嘗試使用 pprint.pprint(obj) 讓版面漂亮一點\n"""
            
        # 將字串轉回 Notebook 要求的陣列格式（以 \n 分隔每一行）
        lines = source.split("\n")
        cell["source"] = [line + "\n" for line in lines[:-1]] + ([lines[-1]] if lines[-1] else [])

# 3. 回存並覆蓋原本的筆記本 (產生學生練習版)
with open(original_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
    
print("學生練習用 Cell 編輯完成！所有輸出皆已清空並替換為 TODO 挖空設計。")
