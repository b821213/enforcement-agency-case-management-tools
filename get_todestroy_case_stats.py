from func_lib import login, get_todestroy_case_stats, get_ended_case_stats
from secret import username_file_manager, password_file_manager
from configs import complete_dept_list

def live_print(string, file_path, **kargs):
	with open(file_path, 'a', encoding='utf-8-sig') as f:
		print (string, file=f, **kargs)

def get_numbers(session, year, end_code, keepterm):
	from datetime import date, timedelta
	cur_date = date(year + 1911, 1, 1)
	one_day = timedelta(days=1)
	dept_exec_nos = {}
	while cur_date.year != year + 1 + 1911:
		end_file_nos = {
			datum['END_FILE_NO'] for datum in get_todestroy_case_stats(
			session, a98_end_code=end_code, keepterm=keepterm,
			ended_date_s=(year, cur_date.month, cur_date.day),
			ended_date_e=(year, cur_date.month, cur_date.day))}
		for end_file_no in end_file_nos:
			a98_exec_t = int(end_file_no[10:12])
			a98_ended_y = int(end_file_no[12:15])
			a98_exec_n = int(end_file_no[15:])
			fail_count = 0
			while fail_count < 3:
				try:
					case_list = get_ended_case_stats(
						session, a98_end_code=end_code, a98_exec_t=a98_exec_t,
						a98_ended_y=a98_ended_y, a98_exec_n1=a98_exec_n)
					for case in case_list:
						cur_dept = case['DEPT_NO']
						if cur_dept not in dept_exec_nos:
							dept_exec_nos[cur_dept] = set()
						dept_exec_nos[cur_dept].add(case['EXEC_NO'])
					break
				except:
					fail_count += 1
			if fail_count == 3:
				print ('error at: ', end_file_no)
				raise RuntimeError
		cur_date += one_day
	return {dept: len(dept_exec_nos[dept]) for dept in dept_exec_nos}

def read_matrix(file_path):
	try:
		with open(file_path, 'r', encoding='utf-8-sig') as f:
			lines = f.read()[:-1].split('\n')
	except:
		return []
	f = lambda x: int(x) if x.isdigit() else x
	return [list(map(f, line.split(','))) for line in lines]

if __name__ == '__main__':
	year = int(input('請輸入查詢年度: '))
	f_out = '%d_todestroy_stats.csv' % year
	session = login(username_file_manager, password_file_manager)
	dept_list = complete_dept_list
	column_titles = ['分類號', '保存年限', '可銷毀日'] + dept_list + ['總件數']
	end_code_list = [
		8020202, 8020301, 8020302, 8020401, 8020402, 8020500,
		8020600, 8020800, 8020900, 8021000, 8030000]
	keepterm = [5, 5, 3, 3, 1, 3, 1, 1, 1, 1, 5]
	mat = read_matrix(f_out)
	if len(mat) == 0:
		live_print (','.join(column_titles), f_out)
		start = 0
	else:
		start = len(mat) - 1
	for end_code, kt in list(zip(end_code_list, keepterm))[start:]:
		print ('正在查詢 %08d 的案件...' % end_code)
		dept_count = get_numbers(session, year, end_code, keepterm)
		live_print ('%08d,%d年,%03d.%02d.%02d,' %
			(end_code, kt, year + kt + 1, 1, 1), f_out, end='')
		for dept in dept_list:
			value = dept_count.get(dept)
			if value is None:
				value = 0
			live_print ('%d,' % value, f_out, end='')
		live_print ('%d' % sum(dept_count.values()), f_out)
	mat = read_matrix(f_out)
	live_print ('合計,,,', f_out, end='')
	for i in range(3, 3 + len(dept_list) + 1):
		live_print ('%d,' % sum([row[i] for row in mat[1:]]), f_out, end='')
