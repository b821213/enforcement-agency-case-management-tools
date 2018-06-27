from func_lib import login, get_case_stats, get_detainable_list
from secret import username_default, password_default
import sys

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [股別] [輸出檔名 (.txt)]')
		sys.exit(0)
	session = login(username_default, password_default)
	data = get_detainable_list(session, sys.argv[1])
	f_out = open(sys.argv[2], 'w')
	print (','.join(['義務人統編', '案件數', '尚欠金額', '金融餘額']), file=f_out)
	for datum in data:
		uid = datum['DUTY_IDNO'].strip()
		cases = get_case_stats(session, uid=uid)
		n_cases = len(set([case['MAIN_EXEC_NO'] for case in cases]))
		undo = int(datum['UNDOMONEY'].replace(',', ''))
		balance = int(datum['BALANCE_AMT'].replace(',', ''))
		print ('%s,%d,%d,%d' % (uid, n_cases, undo, balance), file=f_out)