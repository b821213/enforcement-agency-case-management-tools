from func_lib import login, get_case_borrowed
from secret import username_file_manager, password_file_manager
import sys

def get_formated_date(title):
	import re
	date_checker = re.compile(r'\d{2,3}\-\d{1,2}\-\d{1,2}$')
	while True:
		date = input('請輸入'+title+'日期 (格式:民國年-月-日): ')
		match = date_checker.match(date)
		if match is not None:
			date = date.split("-")
			return date[0] + '{:02d}'.format(int(date[1])) + '{:02d}'.format(int(date[2]))
		else:
			print ('日期格式錯誤，應為:民國年-月-日\n')

def decoded_mixed_end_file_no(end_file_no):
	"""
	decode mixed end_file_no like 'CY08020302031050053676' and '091CY0109500057758'
	"""
	before_98 = end_file_no[:3].isdigit()
	get_exec_year = (lambda data:
		data[:3] if before_98 else '')
	get_ended_year = (lambda data:
		data[7:10] if before_98 else data[12:15])
	get_type = (lambda data:
		data[5:7] if before_98 else data[10:12])
	get_series_number = (lambda data:
		data[-8:] if before_98 else data[-7:])
	get_end_code = (lambda data:
		'' if before_98 else data[2:10])
	return {
		'END_FILE_EXEC_YEAR': get_exec_year(end_file_no),
		'END_FILE_ENDED_YEAR': get_ended_year(end_file_no),
		'END_FILE_CASE': get_type(end_file_no),
		'END_FILE_SERIAL_NUM': get_series_number(end_file_no),
		'END_CODE': get_end_code(end_file_no),
	}

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print ('使用說明: python [本程式名稱] [輸出檔名 (.csv)]')
		sys.exit(0)
	session = login(username_file_manager, password_file_manager)
	date_start = get_formated_date('開始')
	date_end = get_formated_date('結束')
	borrowed = get_case_borrowed(session, date_start, date_end)
	print("案件查詢完成。\n")
	with open(sys.argv[1], 'w', encoding='utf-8-sig') as f:
		print (','.join([
			'執行案號', '件數', '歸檔檔號', '執行年度(98舊格式)', '歸檔年度', 
			'案件分類', '歸檔類別', '檔號', '義務人', '借調申請日期', '借調人代碼', 
			'借調人姓名', '借調人股別', '出庫日期', '應還日期', '延還次數', 
			'延還後應還日期', '實際還卷日期']), file=f)
	
	for index, case in enumerate(borrowed):
		end_file_no = borrowed[index]['END_FILE_NO']
		data = decoded_mixed_end_file_no(end_file_no)
		with open(sys.argv[1], 'a', encoding='utf-8-sig') as f:
			strings = (
				#result['END_FILE_NO_STR'],
				borrowed[index]['EXEC_YEAR'] + '-' + borrowed[index]['EXEC_RECTYPE'] + borrowed[index]['EXEC_CASE'] + '-' + borrowed[index]['EXEC_SEQNO'],
				borrowed[index]['COUNT_TOTAL'],
				borrowed[index]['END_FILE_NO_STR'],
				data['END_FILE_EXEC_YEAR'],
				data['END_FILE_ENDED_YEAR'],
				data['END_FILE_CASE'],
				data['END_CODE'],
				data['END_FILE_SERIAL_NUM'],
				borrowed[index]['DUTY_NAME'].replace(',', '、'),
				borrowed[index]['APPLY_DATE'],
				borrowed[index]['LOANMANNO'],
				borrowed[index]['LOANMANNAME'],
				borrowed[index]['LOANUNIT'],
				borrowed[index]['OUT_DATE'],
				borrowed[index]['SBACK_DATE'],
				borrowed[index]['DELAY_NUM'],
				borrowed[index]['DELAY_DATE'],
				borrowed[index]['RBACK_DATE'])
			print (','.join(strings), file=f)