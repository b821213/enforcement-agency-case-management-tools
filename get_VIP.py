from func_lib import login, get_case_stats
from share_lib import ranged_case_list, print_for_merge
import sys
from secret import username_default, password_default
from time import localtime as lt

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [股別] [輸出檔名 (.txt)]')
		sys.exit(0)
	dept = sys.argv[1]
	target = int(input('想找多案義務人還是大額義務人？(1/多案 2/大額) '))
	if target not in [1, 2]:
		raise ValueError('輸入應為 1 或 2')
	n_cases_lb = int(input('請輸入義務人案件數下限: '))
	n_cases_ub = int(input('請輸入義務人案件數上限 (無上限請打 -1): '))
	money_lb = int(input('請輸入義務人尚欠金額下限: '))
	money_ub = int(input('請輸入義務人尚欠金額上限 (無上限請打 -1): '))
	INF = 1e100
	if n_cases_ub == -1:
		n_cases_ub = INF
	if money_ub == -1:
		money_ub = INF
	MAXN = 400000
	y_begin = lt().tm_year - 4
	y_end = lt().tm_year
	data = []
	session = login(username_default, password_default)
	for y in range(y_begin, y_end + 1):
		for t in range(1, 5):
			print ('正在查詢 %03d-%02d 的案件...' % (y, t))
			counter = 3
			success = False
			err_type = None
			err_args = None
			while not success and counter > 0:
				try:
					data += get_case_stats(
						session, exec_y=y, exec_t=t, exec_n1=1, exec_n2=MAXN,
						dept=dept)
				except Exception as e:
					err_type = type(e)
					err_args = e.args
					counter -= 1
				else:
					success = True
			if counter == 0:
				print ('%r %s' % (err_type, err_args))
				sys.exit(0)
	uids = set([datum['DUTY_IDNO'].strip() for datum in data])
	cases_by_uid = {}
	for_sorting = []
	for uid in uids:
		cases, summary = get_case_stats(session, uid=uid, summary=True)
		n_cases = len(set([case['MAIN_EXEC_NO'] for case in cases]))
		money = (summary['PAY_AMT_TOTAL']
			- summary['RECEIVE_AMT_TOTAL']
			- summary['RETURN_AMT_TOTAL']
			- summary['RETURN_AMT_NO_TOTAL']
			- summary['EVI_AMT_TOTAL']
			- summary['PAY_AMT_RETURN_TOTAL'])
		if (n_cases_lb <= n_cases <= n_cases_ub and
			money_lb <= money <= money_ub):
			cases_by_uid[uid] = cases
			for_sorting.append((uid, n_cases, money))
	results = sorted(for_sorting, key=lambda x: x[target], reverse=True)
	with open(sys.argv[2], 'w', encoding='utf8') as f:
		for uid, n_cases, money in results:
			cases = cases_by_uid[uid]
			print ('%s (%s) 未結案件數 %d 尚欠金額 %d' %
				(cases[-1]['DUTY_NAME'], uid, n_cases, money), file=f)
			print_for_merge(ranged_case_list(cases), f_out=f)