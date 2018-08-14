from func_lib import login, get_ended_case_stats
from secret import username_file_manager, password_file_manager
from datetime import date, timedelta
import sys

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print ('使用說明: python [本程式名稱] [輸出檔名 (.csv)]')
		sys.exit(0)
	session = login(username_file_manager, password_file_manager)
	year = int(input('請輸入查詢年度: '))
	with open(sys.argv[1], 'w', encoding='utf-8-sig') as f:
		print (','.join([
			'檔號', '檔號年分', '類別', '流水號', '分類號', '執行案號', '股別',
			'歸檔日期', '應銷毀日期', '年限', '檔卷狀態']), file=f)
	cur_date = date(year + 1911, 1, 1)
	delta = timedelta(days=1)
	while cur_date.year != year + 1911 + 1:
		converted = (year, *cur_date.timetuple()[1:3])
		print ('正在查詢 %03d/%02d/%02d 歸檔案件...' % converted)
		results = get_ended_case_stats(
			session, in_date_s=converted, in_date_e=converted)
		with open(sys.argv[1], 'a', encoding='utf-8-sig') as f:
			get_year = (lambda data:
				data['END_FILE_NO'][12:15] if year > 98
				else data['END_FILE_NO'][7:10])
			get_type = (lambda data:
				data['END_FILE_NO'][10:12] if year > 98
				else data['END_FILE_NO'][5:7])
			get_series_number = (lambda data:
				data['END_FILE_NO'][-7:] if year > 98
				else data['END_FILE_NO'][-8:])
			get_end_code = (lambda data:
				data['END_FILE_NO'][2:10] if year > 98 else '')
			for result in results:
				strings = (
					result['END_FILE_NO'],
					get_year(result),
					get_type(result),
					get_series_number(result),
					get_end_code(result),
					result['EXEC_NO'],
					result['DEPT_NO'],
					result['END_FILE_DATE'],
					result['SDESTORYDATE'],
					str(int(result['SDESTORYDATE'][0:3]) -
						int(result['END_FILE_DATE'][0:3]) - 1),
					result['FILESTATUS'])
				print (','.join(strings), file=f)
		cur_date += delta
