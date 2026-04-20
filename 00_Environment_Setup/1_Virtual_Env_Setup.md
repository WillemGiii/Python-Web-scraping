# 虛擬環境建置指南

本指南將帶您一步步在專案中建立並設定 Python 虛擬環境，並安裝 `requirements.txt` 中所列的相關套件。

### 步驟一 : 建立環境
使用 Python 3.12 建立名為 `.venv` 的虛擬環境：
```bash
py -3.12 -m venv .venv
```

### 步驟二 : 啟動環境
必須「啟動」才能讓終端機指令指向虛擬環境，而非全域。
```bash
.\.venv\Scripts\activate.bat
```
> **成功指標** : 終端機提示字元前方有出現 `(.venv)` 字樣。

### 步驟三 : 更新套件管理工具 pip 自身
確保您使用的是最新版的 pip：
```bash
python.exe -m pip install --upgrade pip
```

### 步驟四 : 切換工作目錄
將當前的工作目錄切換到名為 `00_Environment_Setup` 的資料夾內：
```bash
cd 00_Environment_Setup 
```

### 步驟五 : 批次安裝清單中的所有套件
透過 `requirements.txt` 一次安裝專案所需的所有套件：
```bash
pip install -r requirements.txt 
```
