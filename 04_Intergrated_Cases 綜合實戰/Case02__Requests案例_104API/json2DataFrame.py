import json
import pandas as pd

file_path = input("輸入要轉檔的JSON檔案:")

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 將 JSON 資料結構轉換為 DataFrame (處理所有的 列 與 行)
df = pd.json_normalize(data)

# 匯出成 CSV 檔案 (設定 index=False 避免多餘的索引行 ，並使用 utf-8-sig 確保 Excel 讀取正常)
df.to_csv('python_jobs.csv', index=False, encoding='utf-8-sig')

print(f"已經json檔{file_path}轉成csv")