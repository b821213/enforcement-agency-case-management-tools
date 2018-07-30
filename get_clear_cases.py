from func_lib import login, get_case_stats, get_topay_summary
from share_lib import (
	is_li_case, ranged_case_list, print_for_merge, get_topay_single)
from secret import username_default, password_default
from configs import max_case_seqno
import sys

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [股別] [輸出檔名 (.txt)]')
		sys.exit(0)
	dept = sys.argv[1]
	exec_t = int(input('請輸入案件種類 (1/2/3/4): '))
	year_begin = int(input('請輸入起始年分: '))
	year_end = int(input('請輸入截止年分: '))
	if exec_t == 4:
		LI_option = int(input('一般費執還是勞保？ (1/排除勞保 2/只印勞保)'))
		if LI_option not in [1, 2]:
			raise ValueError('輸入應為 1 或 2')
	session = login(username_default, password_default)
	cases = []
	for exec_y in range(year_begin, year_end + 1):
		cases += get_case_stats(
			session, exec_y=exec_y, exec_t=exec_t,
			exec_n1=1, exec_n2=max_case_seqno, dept=dept)
	main_to_all = {}
	for case in cases:
		if exec_t == 4 and LI_option == 1 and is_li_case(case):
			continue
		elif exec_t == 4 and LI_option == 2 and not is_li_case(case):
			continue
		main_num = case['MAIN_EXEC_NO']
		if main_num not in main_to_all:
			main_to_all[main_num] = []
		main_to_all[main_num].append(case)
	to_print = []
	for main_num, cases in main_to_all.items():
		try:
			if len(cases) == 1:
				topay = get_topay_single(session, cases[0])
			else:
				# The cases must be HI or LI
				topay = get_topay_summary(
					session, exec_y=cases[0]['EXEC_YEAR'],
					exec_t=cases[0]['EXEC_CASE'], exec_n1=cases[0]['EXEC_SEQNO'],
					exec_n2=cases[-1]['EXEC_SEQNO'])
			if topay == 0:
				to_print += cases
		except Exception as e:
			if len(cases) == 1:
				num_str = '%03d-%02d-%08d' % (
					cases[0]['EXEC_YEAR'], cases[0]['EXEC_CASE'],
					cases[0]['EXEC_SEQNO'])
			else:
				num_str = '%03d-%02d-%08d~%08d' % (
					cases[0]['EXEC_YEAR'], cases[0]['EXEC_CASE'],
					cases[0]['EXEC_SEQNO'], cases[-1]['EXEC_SEQNO'])
			print ('處理 %s 時遇到錯誤' % num_str)
			print (e.__repr__())
	with open(sys.argv[2], 'w') as f:
		print_for_merge(ranged_case_list(to_print), f_out=f)
