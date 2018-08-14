import os
from secret import *
import re

def write_back(settings):
	with open('configs.py', 'w', encoding='utf8') as f:
		for key, value in settings.items():
			print ('%s = %r' % (key, value), file=f)

def set_default_dept(session, settings):
	from func_lib import get_default_dept_list
	default_dept_list = get_default_dept_list(session)
	index = 0
	if len(default_dept_list) > 1:
		print ('偵測到多個股別的權限:', end='')
		for i, dept in enumerate(default_dept_list):
			if i % 5 == 0:
				print ('')
			print ('\t%02d) %s' % (i + 1, dept), end='')
		print ('')
		while True:
			input_str = input('請填入要做為預設股別的股別代號 (%d~%d): ' %
				(1, len(default_dept_list)))
			if (input_str.isdigit() is True and
				1 <= int(input_str) <= len(default_dept_list)):
				index = int(input_str)
				break
			else:
				print ('請輸入 %d~%d 間的整數' % (1, len(default_dept_list)))
	settings['default_dept'] = default_dept_list[index - 1]

def find(name, path):
	for root, dirs, files in os.walk(path):
		if name in files:
			return os.path.join(root, name)
	return None

def set_adobe_reader_path(settings):
	name = 'AcroRd32.exe'
	path = find(name, r'C:\\')
	if path is None:
		print ('自動偵測 Adobe Reader 執行檔位置失敗...')
		path = input('請手動填入執行檔位置: ')
	settings['adobe_reader_path'] = path

def set_default_tmp_file_path(settings):
	cwd = os.getcwd()
	directory = cwd + r'\tmp_dir'
	if not os.path.exists(directory):
		os.makedirs(directory)
	settings['default_asset_page_path'] = directory + r'\tmp_asset.pdf'
	settings['default_bank_response_path'] = directory + r'\tmp_508.pdf'
	settings['default_payment_list_path'] = directory + r'\tmp_payment.pdf'

def set_default_asset_date_begin(settings):
	date_checker = re.compile(r'\d{7}$')
	while True:
		input_str = input('請輸入財產清冊查詢起始日 (YYYMMDD): ')
		if date_checker.match(input_str) is None:
			print ('請輸入正確格式，如 1070101。')
		else:
			settings['asset_date_begin'] = input_str
			break

def set_current_dept_list(session, settings):
	from func_lib import get_default_dept_list
	settings['current_dept_list'] = get_default_dept_list(session)

def set_complete_dept_list(session, settings):
	from func_lib import get_complete_dept_list
	settings['complete_dept_list'] = get_complete_dept_list(session)

if __name__ == '__main__':
	with open('configs_default.py', 'r', encoding='utf-8-sig') as f:
		settings = eval(f.read())
	# Gets server IP address to login first
	ip_checker = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
	while True:
		input_str = input('請輸入案管主機 IP: ')
		match = ip_checker.match(input_str)
		if match is not None:
			settings['server_ip_addr'] = input_str
			break
		else:
			print ('IP 形如 xxx.xxx.xxx.xxx，其中 xxx 為 0~255 間的整數。')
	# Writes back server_ip_addr first to enable web functions.
	write_back(settings)
	from func_lib import login
	if username_default != '':
		session = login(username_default, password_default)
		if session is None:
			print (
				'執行人員帳號密碼 '
				'(username_default, password_default) 設定錯誤。')
		else:
			print ('設定預設股別...')
			set_default_dept(session, settings)
			print ('設定 Adobe Reader 執行檔路徑...')
			set_adobe_reader_path(settings)
			print ('設定暫存檔路徑...')
			set_default_tmp_file_path(settings)
			print ('設定財產清冊查詢起始日...')
			set_default_asset_date_begin(settings)
			write_back(settings)
			print ('執行人員設定完畢！')
	if username_file_manager != '':
		session = login(username_file_manager, password_file_manager)
		if session is None:
			print (
				'檔管人員帳號密碼 '
				'(username_file_manager, password_file_manager) 設定錯誤。')
		else:
			print ('設定當前股別列表...')
			set_complete_dept_list(session, settings)
			write_back(settings)
			print ('檔管人員設定完畢！')
	if username_stats_manager != '':
		session = login(username_stats_manager, password_stats_manager)
		if session is None:
			print (
				'統計人員帳號密碼 '
				'(username_stats_manager, password_stats_manager) 設定錯誤。')
		else:
			print ('設定歷年股別列表...')
			set_current_dept_list(session, settings)
			write_back(settings)
			print ('統計人員設定完畢！')
