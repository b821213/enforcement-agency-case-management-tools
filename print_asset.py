from func_lib import login, get_case_details, download_asset_page
from share_lib import read_input
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
	for index, uid_or_seqno in enumerate(case_list):
		if type(uid_or_seqno) is tuple:
			y, t, n = uid_or_seqno
			uid = None
		else:
			uid = uid_or_seqno
			y, t, n = None, None, None
		details = get_case_details(
			session, exec_y=y, exec_t=t, exec_n=n, uid=uid)
		name = details['DUTY_NAME']
		uid_list = details['DUTY_IDNO']
		try:
			print ('(%d/%d)%s %s (%s) ' % (
				index + 1, len(case_list),
				'' if (y, t, n) == (None, None, None)
				else ' [%03d-%02d-%08d]' % (y, t, n),
				name, str(uid_list)[1:-1].replace("'", '')), end='')
			if download_asset_page(session, password_asset, uid_list) is False:
				raise Exception('下載失敗')
			print ('列印中')
			proc = subprocess.Popen(
				[adobe_reader_path, '/t', default_asset_page_path])
			sleep(asset_wait_time)
			proc.kill()
		except Exception as e:
			print (e)
			undo.append((y, t, n, uid_list))
	if len(undo) > 0:
		print ('未列印清單:')
		for y, t, n, uid_list in undo:
			print ('\t%03d-%02d-%08d (%s) ' % (
				y, t, n, str(uid_list)[1:-1].replace("'", '')))