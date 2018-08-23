from func_lib import (
	login, get_case_details, get_asset_page, download_asset_page)
from share_lib import read_input, print_and_record
from secret import username_default, password_default, password_asset
from configs import adobe_reader_path, default_asset_page_path, asset_wait_time
import sys
import subprocess
from time import sleep

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [紀錄檔名 (.csv)]')
		sys.exit(0)
	session = login(username_default, password_default)
	input_list = read_input(sys.argv[1])
	f_err = open(sys.argv[2], 'w', encoding='utf-8-sig')
	for index, uid_or_seqno in enumerate(input_list):
		if type(uid_or_seqno) is tuple:
			y, t, n = uid_or_seqno
			uid = ''
			input_str = '%03d-%02d-%08d' % (y, t, n)
		else:
			uid = uid_or_seqno
			y, t, n = None, None, None
			input_str = uid
		print ('(%d/%d) %s 查詢中...' %
			(index + 1, len(input_list), input_str))
		details = get_case_details(
			session, exec_y=y, exec_t=t, exec_n=n, uid=uid)
		if details is None:
			print_and_record ('%s,請確認閱讀權限' % input_str, file=f_err)
			continue
		name = details['DUTY_NAME']
		uid_list = details['DUTY_IDNO']
		if download_asset_page(session, password_asset, uid_list) is False:
			if len(get_asset_page(session, password_asset, uid_list)) == 0:
				print_and_record('%s,查無財產資料' % input_str, file=f_err)
			else:
				print_and_record('%s,下載失敗' % input_str, file=f_err)
			continue
		proc = subprocess.Popen(
			[adobe_reader_path, '/t', default_asset_page_path])
		sleep(asset_wait_time)
		proc.kill()
	f_err.close()
