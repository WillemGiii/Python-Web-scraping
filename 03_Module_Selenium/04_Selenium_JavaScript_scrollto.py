import time
from selenium import webdriver
def infinite_scroll(driver, pause_time=2):
	'''
	使用 JavaScript 高度偵測的無限捲動方案
	Args : 
		driver : WebDriver instance
		pause_time: 等待載入的時間 (秒)
	'''
	# 1. 取得當前頁面高度
	last_height = driver.execute_script(" return document.body.scrollHeight ")
	
	while True :
		 # 2. 捲動到底部
		 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		 
		 # 3. 等待頁面載入
		 time.sleep(pause_time)
		 
		 # 4. 計算新的頁面高度
		 new_height = driver.execute_script("return document.body.scrollHeight")
		 
		 # 5. 比對高度是否改變
		 if new_height == last_height:
			 print("已抵達頁面底部")
			 break
		 
		 # 更新高度基準
		 last_height = new_height
		 print(f"目前頁面高度 : {last_height}px")
 
 #使用範例
if __name__ =="__main__":
    driver = webdriver.Chrome()
    driver.get("https://ai.ettoday.net/")
    infinite_scroll(driver)