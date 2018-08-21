from configs import complete_dept_list
import sys

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [輸出檔名 (.csv)]')
		sys.exit(0)
	while True:
		year = input('請輸入年份: ')
		if year.isdigit() is True:
			year = int(year)
			break
		else:
			print ('請檢查輸入格式是否正確。')
	while True:
		deadline = input('欲銷毀應銷毀日期在何日(含)以前的案件？(yyymmdd) ')
		if len(deadline) == 7 and deadline.isdigit() is True:
			break
		else:
			print ('請檢查輸入格式是否正確。')
	stats = {}
	dept_case = {}
	print ('讀取輸入檔中...')
	with open(sys.argv[1], 'r', encoding='utf-8-sig') as f:
		for index, line in enumerate(f):
			if index == 0:
				case_list_title = line
			else:
				s = line.split(',')
				end_code = s[5]
				dept = s[7]
				todestroy_date = s[9]
				# s[4] is end_code
				if s[9] > deadline:
					continue
				key = (end_code, dept)
				stats[key] = stats.setdefault(key, 0) + 1
				dept_case.setdefault(dept, []).append(line)
	dept_list = complete_dept_list
	# Creates files for case list per dept.
	file_path_prefix = sys.argv[1].split('.')[0]
	for dept in dept_list:
		file_path = file_path_prefix + '_' + dept + '.csv'
		print ('生成 %s 股案件清單中...' % dept, end='\r')
		with open(file_path, 'w', encoding='utf-8-sig') as f:
			print (case_list_title, end='', file=f)
			for line in dept_case.setdefault(dept, []):
				print (line, end='', file=f)
	column_titles = ['分類號', '保存年限', '可銷毀日'] + dept_list + ['總件數']
	end_code_list = [
		8020202, 8020301, 8020302, 8020401, 8020402, 8020500,
		8020600, 8020800, 8020900, 8021000, 8030000]
	keepterm_list = [5, 5, 3, 3, 1, 3, 1, 1, 1, 1, 5]
	print ('\n生成統計表格中...')
	with open(sys.argv[2], 'w', encoding='utf-8-sig') as f:
		print (','.join(column_titles), file=f)
		for end_code, keepterm in zip(end_code_list, keepterm_list):
			total = 0
			print ('="%08d",%d年,%03d.%02d.%02d,' %
				(end_code, keepterm, year + keepterm + 1, 1, 1),
				end='', file=f)
			for dept in dept_list:
				size = stats.get(('%08d' % end_code, dept), 0)
				total += size
				print ('%d,' % size, end='', file=f)
			print ('%d' % total, file=f)
		print ('合計,,,', end='', file=f)
		total = 0
		for dept in dept_list:
			size = sum(
				[stats.get(('%08d' % end_code, dept), 0)
				for end_code in end_code_list])
			total += size
			print ('%d,' % size, end='', file=f)
		print ('%d' % total, file=f)
