from func_lib import login, get_asset_page, get_case_details, get_case_stats
from share_lib import read_input
from secret import username_default, password_default, password_asset
from configs import asset_date_begin
import sys

def refined_asset_list(session, uid):
	data = get_asset_page(
		session, password_asset, uid, date_begin=asset_date_begin)
	useful_data = {}
	# Health insurance data should be handled separately because the latter
	# data can replace the former data even when their UNIT_NM are not the same.
	hi_data = None
	for datum in data:
		key = (datum['INCOME_DESC'], datum['UNIT_NM'], datum['IDN_BAN'])
		exchange_rate = (
				1 if datum['MONEY_RATE'] == ''
				else float(datum['MONEY_RATE']))
		amount = (
				0 if datum['AMT'] == ''
				else int(datum['AMT'].replace(',', '')))
		value = (datum['IMP_DATE'], int(exchange_rate * amount))
		if datum['INCOME_DESC'] == '健保投保單位':
			if hi_data is None or hi_data[1][0] < value[0]:
				hi_data = (key, value)
		else:
			if key in useful_data:
				if useful_data[key][0] < value[0]:
					useful_data[key] = value
			else:
				useful_data[key] = value
	if hi_data is not None:
		useful_data[hi_data[0]] = hi_data[1]
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
	output = open(sys.argv[2], 'w', encoding='utf-8-sig')
	case_list = read_input(sys.argv[1])
	for index, uid_or_seqno in enumerate(case_list):
		if type(uid_or_seqno) is tuple:
			y, t, n = uid_or_seqno
			uid = ''
			print ('(%d/%d) %03d-%02d-%08d 查詢中' %
				(index + 1, len(case_list), y, t, n))
		else:
			uid = uid_or_seqno
			y, t, n = None, None, None
			print ('(%d/%d) %s 查詢中' %
				(index + 1, len(case_list), uid))
		details = get_case_details(
			session, exec_y=y, exec_t=t, exec_n=n, uid=uid)
		name = details['DUTY_NAME']
		uid_list = details['DUTY_IDNO']
		is_wholly_owned = details['IS_WHOLLY_OWNED']
		is_partnership = details['IS_PARTNERSHIP']
		if is_wholly_owned is True:
			name = '(獨資) ' + name
		if is_partnership is True:
			name = '(合夥) ' + name
		summary = get_case_stats(session, uid=uid_list[0], summary=True)[1]
		topay = (summary['PAY_AMT_TOTAL'] - summary['RECEIVE_AMT_TOTAL']
			- summary['RETURN_AMT_TOTAL'] - summary['RETURN_AMT_NO_TOTAL']
			- summary['EVI_AMT_TOTAL'] - summary['PAY_AMT_RETURN_TOTAL'])
		to_print = []
		to_print.append(','.join([
			'%03d-%02d-%08d' % (y, t, n) if type(uid_or_seqno) is tuple else '',
			'"%s (%s)"' % (name, str(uid_list)[1:-1].replace("'", '')),
			'%s' % '尚欠金額', '%d' % topay]))
		asset_list = refined_asset_list(session, uid_list)
		for item in asset_list:
			to_print.append(','.join(map(str, item)))
		for line in to_print:
			if flip_flop == 0:
				print (line + ',' * 4, file=output)
			else:
				print (',' * 4 + line, file=output)
		flip_flop = 1 - flip_flop
