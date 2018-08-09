# 使用者股別
default_dept = ''
default_page_size = 1000000
# 案管系統主機 IP (以英文句號分隔的 4 個 0~255 間的數值)
server_ip_addr = ''
browser_version = (
	'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)'
	' Chrome/67.0.3396.62 Safari/537.36')
# print_asset_page.py 財冊暫存檔路徑 (.../*.pdf)
default_asset_page_path = ''
# print_bank_response.py 銀行回覆暫存檔路徑 (.../*.pdf)
default_bank_response_path = ''
# print_payment_list.py 繳款金額暫存檔路徑 (.../*.pdf)
default_payment_list_path = ''
# adobe reader 執行檔路徑 (.../*.exe)
adobe_reader_path = ''
# 財冊預設起始日期 (%03d%02d%02d)
asset_date_begin = ''
# 自動印財冊間隔時間 (單位: 秒)
asset_wait_time = 5
# 自動印金融回覆間隔時間 (單位: 秒)
bank_wait_time = 5
# 自動印繳款金額間隔時間 (單位: 秒)
payment_wait_time = 5
# 進行簿顯示條目數量
n_show_situ_items = 5
# 單年單一類別案號最大值
max_case_seqno = 400000
# 當前執行股別清單
current_dept_list = [
	'乙', '丁', '仁', '平', '甲', '孝', '和',
	'忠', '信', '愛', '義', '德', '禮'
]
