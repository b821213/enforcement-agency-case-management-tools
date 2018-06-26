from func_lib import login, read_input, get_case_stats, download_asset_page
from secret import username_default, password_default, password_asset
from configs import adobe_reader_path, default_asset_page_path, asset_wait_time
import sys
import subprocess
from time import sleep

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)]')
		sys.exit(0)
	session = login(username_default, password_default)
	undo = []
	case_list = read_input(sys.argv[1])
	for index, (y, t, n) in enumerate(case_list):
		try:
			case_data = get_case_stats(session, exec_y=y, exec_t=t, exec_n1=n)
			uid = case_data[0]['DUTY_IDNO'].strip()
			print ('(%d/%d) %03d-%02d-%08d (%s) ' %
				(index + 1, len(case_list), y, t, n, uid), end='')
			if download_asset_page(session, password_asset, uid) is False:
				raise Exception('下載失敗')
			print ('列印中')
			proc = subprocess.Popen(
				[adobe_reader_path, '/t', default_asset_page_path])
			sleep(asset_wait_time)
			proc.kill()
		except Exception as e:
			print (e)
			undo.append((y, t, n, uid))
	if len(undo) > 0:
		print ('未列印清單:')
		for u in undo:
			print ('\t%03d-%02d-%08d (%s) ' % u)