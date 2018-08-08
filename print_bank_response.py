from func_lib import login, download_bank_response
from share_lib import read_input
from secret import username_default, password_default
from configs import adobe_reader_path, default_bank_response_path, bank_wait_time
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
			uid = ''
			input_str = '%03d-%02d-%08d' % (y, t, n)
		else:
			uid = uid_or_seqno
			y, t, n = None, None, None
			input_str = uid
		try:
			print ('(%d/%d) %s ' % (
				index + 1, len(case_list), input_str), end='')
			if download_bank_response(
				session, exec_y=y, exec_t=t, exec_n=n, uid=uid) is False:
				raise Exception('下載失敗')
			print ('列印中')
			proc = subprocess.Popen(
				[adobe_reader_path, '/t', default_bank_response_path])
			sleep(bank_wait_time)
			proc.kill()
		except Exception as e:
			print (e)
			undo.append(input_str)
	if len(undo) > 0:
		print ('未列印清單:')
		for input_str in undo:
			print ('\t%s' % input_str)
