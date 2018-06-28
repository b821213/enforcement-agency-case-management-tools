from func_lib import login, read_input
from func_lib import get_asset_page, get_case_stats, get_topay_summary
from secret import username_default, password_default, password_asset
from configs import asset_date_begin
import sys

def get_duty_name_and_uid(session, exec_y, exec_t, exec_n):
	data = get_case_stats(
		session, exec_y=exec_y, exec_t=exec_t, exec_n1=exec_n, noendbox=False)
	return data[-1]['DUTY_NAME'], data[-1]['DUTY_IDNO']

def refined_asset_list(session, uid):
	data = get_asset_page(
		session, password_asset, uid, date_begin=asset_date_begin)
	useful_data = {}
	for datum in data:
		key = (datum['INCOME_DESC'], datum['UNIT_NM'], datum['IDN_BAN'])
		exchange_rate = (
				1 if datum['MONEY_RATE'] == ''
				else float(datum['MONEY_RATE']))
		amount = (
				0 if datum['AMT'] == '' 
				else int(datum['AMT'].replace(',', '')))
		value = (datum['IMP_DATE'], int(exchange_rate * amount))
		if key in useful_data:
			if useful_data[key][0] < value[0]:
				useful_data[key] = value
		else:
			useful_data[key] = value
	ret_list = []
	for key, value in useful_data.items():
		if value[1] >= 450:
			ret_list.append((*key[:2], *value))
	return ret_list

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [輸出檔名 (.csv)]')
		sys.exit(0)
	session = login(username_default, password_default)
	flip_flop = 0
	output = open(sys.argv[2], 'w', encoding='utf8')
	case_list = read_input(sys.argv[1])
	for index, (y, t, n) in enumerate(case_list):
		print ('(%d/%d) %03d-%02d-%08d 查詢中' % 
			(index + 1, len(case_list), y, t, n))
		name, uid = get_duty_name_and_uid(session, y, t, n)
		topay = get_topay_summary(session, uid=uid)
		to_print = []
		to_print.append(','.join([
			'%03d-%02d-%08d' % (y, t, n),
			'%s (%s)' % (name, uid),
			'%s' % '尚欠金額',
			'%d' % get_topay_summary(session, uid=uid)]))
		asset_list = refined_asset_list(session, uid)
		for item in asset_list:
			to_print.append(','.join(map(str, item)))
		for line in to_print:
			if flip_flop == 0:
				print (line + ',' * 4, file=output)
			else:
				print (',' * 4 + line, file=output)
		flip_flop = 1 - flip_flop