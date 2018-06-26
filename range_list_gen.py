from func_lib import login, get_case_stats
from secret import username_default, password_default

import sys
 
if __name__ == '__main__':
	if len(sys.argv) != 7:
		print ('使用說明: python [本程式名稱] [輸出檔名 (.csv)] [股別] [年度] [案件類別] [區間起始號] [區間結束號]')
		sys.exit(0)
	dept = sys.argv[2]
	y, t, n1, n2 = map(int, sys.argv[3:])
	session = login(username_default, password_default)
	data = get_case_stats(session, exec_y=y, exec_t=t, exec_n1=n1, exec_n2=n2, dept=dept)
	with open(sys.argv[1], 'w') as f:
		for d in data:
			print ('%s,%s,%s' % (d['EXEC_YEAR'], d['EXEC_CASE'], d['EXEC_SEQNO']), file=f)