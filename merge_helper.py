from func_lib import login, read_input, get_case_stats, get_topay_summary
from secret import username_default, password_default
import sys

def is_hi_case(case):
	return case['EXEC_CASE'] == '02'

def is_li_case(case):
	return case['SEND_ORG_ID'] == '107001'

def is_hi_or_li_case(case):
	return is_hi_case(case) or is_li_case(case)

def ranged_case_list(case_list):
	cur_last = (-1, -1, -1)
	cur_left = (-1, -1, -1)
	ret_list = []
	for case in case_list:
		y = int(case['EXEC_YEAR'])
		t = int(case['EXEC_CASE'])
		n = int(case['EXEC_SEQNO'])
		if (y != cur_last[0] or t != cur_last[1] or n != cur_last[2] + 1):
			ret_list.append((*cur_left, cur_last[2], cur_last[-1]))
			cur_left = (y, t, n)
		cur_last = (y, t, n, '*' if is_hi_or_li_case(case) else '')
	ret_list.append((*cur_left, cur_last[2], cur_last[-1]))
	return ret_list[1:]

def print_for_merge(ranged_cl, f_out=sys.stdout):
	data = sorted(ranged_cl, key=lambda x: (x[1], x[0], x[2]))
	to_print = []
	for ranged_n in data:
		if ranged_n[2] == ranged_n[3]:
			to_print.append('%03d-%02d-%06d%7s%s' %
				(*ranged_n[:3], '', ranged_n[-1]))
		else:
			to_print.append('%03d-%02d-%06d~%06d%s' % ranged_n)
	to_print_in_row = []
	for i in range(0, len(to_print), 5):
		to_print_in_row.append(
			'\t' + '\t'.join(to_print[i : i + 5]))
	print ('\n'.join(to_print_in_row), file=f_out)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [輸出檔名 (.txt)]')
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
	f_out = open(sys.argv[2], 'w')
	case_list = read_input(sys.argv[1])
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
			data = get_case_stats(session, uid=uid)
			if hi_print is False:
				data = [datum for datum in data if not is_hi_case(datum)]
			if li_print is False:
				data = [datum for datum in data if not is_li_case(datum)]
			n_cases = len(set([datum['MAIN_EXEC_NO'] for datum in data]))
			title_str += ' 列出件數 %d' % n_cases
			if topay_print is True:
				title_str += ' 尚欠金額 %d' % get_topay_summary(session, uid=uid)
			print (title_str, file=f_out)
			print_for_merge(ranged_case_list(data), f_out=f_out)
			done[uid] = value_str
		else:
			print ('%s 同一義務人已出現於清單中: %s' %
				(title_str, prev), file=f_out)
	f_out.close()