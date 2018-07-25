from func_lib import login, ending_cases
from share_lib import print_and_record
from configs import default_dept
from secret import username_default, password_default
import sys

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [輸出檔名 (.csv)]')
		sys.exit(0)
	session = login(username_default, password_default)
	case_list = []
	f_in = open(sys.argv[1], 'r')
	for line in f_in:
		raw = line[:-1].split(',')
		raw += [''] * (5 - len(raw))
		raw[3] = raw[2][:-len(raw[3])] + raw[3]
		y, t, n1, n2, usr_situ = map(lambda s: None if s == '' else int(s), raw)
		if n2 is None:
			n2 = n1
		for n in range(n1, n2 + 1):
			case_list.append([y, t, n])
	f_in.close()
	suc_count = 0
	f_out = open(sys.argv[2], 'w')
	for y, t, n in case_list:
		suc, msg = ending_cases(session, default_dept, y, t, n, undo=True)
		if suc is True:
			print ('%03d,%02d,%08d,%s' % (y, t, n, msg))
			suc_count += 1
		else:
			print_and_record ('%03d,%02d,%08d,%s' % (y, t, n, msg), file=f_out)
	f_out.close()
	print ('-' * 40)
	print ('成功 %d 件\t失敗 %d 件' % (suc_count, len(case_list) - suc_count))