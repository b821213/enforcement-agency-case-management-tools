from func_lib import login, get_ended_case_stats
from secret import username_file_manager, password_file_manager
from datetime import date, timedelta
import sys

def decoded_end_file_no(end_file_no):
	get_exec_year = (lambda data:
		end_file_no[:3] if year <= 98 else '')
	get_ended_year = (lambda data:
		end_file_no[12:15] if year > 98 else end_file_no[7:10])
	get_type = (lambda data:
		end_file_no[10:12] if year > 98 else end_file_no[5:7])
	get_series_number = (lambda data:
		end_file_no[-7:] if year > 98 else end_file_no[-8:])
	get_end_code = (lambda data:
		end_file_no[2:10] if year > 98 else '')
	return {
		'END_FILE_EXEC_YEAR': get_exec_year(end_file_no),
		'END_FILE_ENDED_YEAR': get_ended_year(end_file_no),
		'END_FILE_CASE': get_type(end_file_no),
		'END_FILE_SERIAL_NUM': get_series_number(end_file_no),
		'END_CODE': get_end_code(end_file_no),
	}

def extracted_dict(data):
	return dict({
		'END_FILE_NO': data['END_FILE_NO'],
		'EXEC_NO': data['EXEC_NO'],
		'DEPT_NO': data['DEPT_NO'],
		'END_FILE_DATE': data['END_FILE_DATE'],
		'DESTROY_DATE': data['SDESTORYDATE'],
		'YEAR_OF_STORAGE': str(
			int(data['SDESTORYDATE'][0:3]) -
			int(data['END_FILE_DATE'][0:3]) - 1),
		'FILE_STATUS': data['FILESTATUS']
	}, **decoded_end_file_no(data['END_FILE_NO']))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print ('使用說明: python [本程式名稱] [輸出檔名 (.csv)]')
		sys.exit(0)
	session = login(username_file_manager, password_file_manager)
	year = int(input('請輸入查詢年度: '))
	end_file_no_set = set()
	cur_date = date(year + 1911, 1, 1)
	delta = timedelta(days=1)
	while cur_date.year != year + 1911 + 1:
		converted = (year, *cur_date.timetuple()[1:3])
		print ('正在查詢 %03d/%02d/%02d 歸檔案件...' % converted, end='\r')
		results = get_ended_case_stats(
			session, in_date_s=converted, in_date_e=converted)
		for result in results:
			data = extracted_dict(result)
			if int(data['END_FILE_ENDED_YEAR']) == year:
				end_file_no_set.add(data['END_FILE_NO'])
		cur_date += delta
	# prints a newline to avoid output from overlap.
	print ('')
	with open(sys.argv[1], 'w', encoding='utf-8-sig') as f:
		print (','.join([
			'檔號', '分案年分 (98前用)', '檔號年分', '類別', '流水號',
			'分類號 (99後用)', '執行案號', '義務人', '股別', '歸檔日期',
			'應銷毀日期', '年限', '檔卷狀態']), file=f)
	for index, end_file_no in enumerate(end_file_no_set):
		print ('正在查詢檔號 %s... (%d/%d)' %
			(end_file_no, index + 1, len(end_file_no_set)), end='\r')
		data = decoded_end_file_no(end_file_no)
		fail_count = 0
		while fail_count < 3:
			try:
				if len(end_file_no) == 18:
					# Cases before 98y
					results = get_ended_case_stats(
						session, b98_exec_y=int(data['END_FILE_EXEC_YEAR']),
						b98_ended_y=int(data['END_FILE_ENDED_YEAR']),
						b98_exec_t=int(data['END_FILE_CASE']),
						b98_exec_n1=int(data['END_FILE_SERIAL_NUM']))
				else:
					results = get_ended_case_stats(
						session, a98_end_code=int(data['END_CODE']),
						a98_exec_t=int(data['END_FILE_CASE']),
						a98_ended_y=int(data['END_FILE_ENDED_YEAR']),
						a98_exec_n1=int(data['END_FILE_SERIAL_NUM']))
				break
			except:
				fail_count += 1
		if fail_count == 3:
			print ('\n讀取檔號 %s 時遭遇錯誤！' % end_file_no)
		else:
			with open(sys.argv[1], 'a', encoding='utf-8-sig') as f:
				for result in results:
					data = decoded_end_file_no(result['END_FILE_NO'])
					strings = (
						result['END_FILE_NO'],
						data['END_FILE_EXEC_YEAR'],
						data['END_FILE_ENDED_YEAR'],
						data['END_FILE_CASE'],
						data['END_FILE_SERIAL_NUM'],
						data['END_CODE'],
						result['EXEC_NO'],
						result['DUTY_NAME'],
						result['DEPT_NO'],
						result['END_FILE_DATE'],
						result['SDESTORYDATE'],
						str(int(result['SDESTORYDATE'][0:3]) -
							int(result['END_FILE_DATE'][0:3]) - 1),
						result['FILESTATUS'])
					print (','.join(strings), file=f)
