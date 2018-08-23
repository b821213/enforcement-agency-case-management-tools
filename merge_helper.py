from func_lib import login, get_case_stats, get_topay_summary
from share_lib import (
	read_input, ranged_case_list, print_for_merge, is_hi_case, is_li_case)
from configs import default_dept
from secret import username_default, password_default
import sys

if __name__ == '__main__':
	if len(sys.argv) != 3 and len(sys.argv) != 4:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)]'
				' [輸出檔名 1 (.txt)] ([輸出檔名 2 (.txt)])')
		sys.exit(0)
	hi_print = None
	li_print = None
	topay_print = None
	while hi_print is None:
		response = input('是否列印健保案件? (y/n)')
		if response == 'y' or response == 'n':
			hi_print = True if response == 'y' else False
	while li_print is None:
		response = input('是否列印勞保案件? (y/n)')
		if response == 'y' or response == 'n':
			li_print = True if response == 'y' else False
	while topay_print is None:
		response = input('是否列出義務人總尚欠金額? (y/n)')
		if response == 'y' or response == 'n':
			topay_print = True if response == 'y' else False
	session = login(username_default, password_default)
	done = {}
	f_out = open(sys.argv[2], 'w', encoding='utf-8-sig')
	case_list = read_input(sys.argv[1])
	output_list_pool = []
	for index, uid_or_seqno in enumerate(case_list):
		if type(uid_or_seqno) is tuple:
			y, t, n = uid_or_seqno
			print ('(%d/%d) %03d-%02d-%08d 查詢中' %
				(index + 1, len(case_list), y, t, n))
			data = get_case_stats(session, exec_y=y, exec_t=t, exec_n1=n)
			uid = data[0]['DUTY_IDNO']
			title_str = '%s-%s-%s (%s)' % (y, t, n, uid)
			value_str = '%s-%s-%s' % (y, t, n)
		else:
			uid = uid_or_seqno
			print ('(%d/%d) %s 查詢中' % (index + 1, len(case_list), uid))
			title_str = '(%s)' % (uid)
			value_str = '%s' % uid
		prev = done.get(uid)
		if prev is None:
			data = get_case_stats(session, uid=uid, dept=default_dept)
			if hi_print is False:
				data = [datum for datum in data if not is_hi_case(datum)]
			if li_print is False:
				data = [datum for datum in data if not is_li_case(datum)]
			n_cases = len(set([datum['MAIN_EXEC_NO'] for datum in data]))
			title_str += ' 未結件數 %d' % n_cases
			if topay_print is True:
				title_str += ' 尚欠金額 %d' % get_topay_summary(session, uid=uid)
			print (title_str, file=f_out)
			rcl = ranged_case_list(session, data)
			if type(uid_or_seqno) is tuple:
				# Removes the input case(s)
				rcl = [datum for datum in rcl
					if not ((y, t) == datum[:2] and datum[2] <= n <= datum[3])]
			print_for_merge(rcl, f_out=f_out)
			output_list_pool += rcl
			done[uid] = value_str
		else:
			print ('%s 同一義務人已出現於清單中: %s' %
				(title_str, prev), file=f_out)
	f_out.close()
	if len(sys.argv) == 4:
		with open(sys.argv[3], 'w') as f:
			print_for_merge(output_list_pool, f_out=f)
