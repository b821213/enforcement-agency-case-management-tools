import requests
import sys
import urls
import configs
from time import localtime as lt

def read_input(file_path):
	f = open(file_path, 'r')
	ret = []
	for line in f:
		data = line[:-1].split(',')
		y, t, n = map(int, data[:3])
		if len(data) == 3 or data[3] is not '':
			ret.append((y, t, n))
	f.close()
	return ret

def formatted(form, value):
	"""This function is only used for simplifying code."""
	return '' if value is None else form % value

def regulized(text):
	to_replace = {
		'true': 'True',
		'false': 'False'
	}
	for key, value in to_replace.items():
		text = text.replace(key, value)
	return text

def today():
	return (lt().tm_year - 1911, lt().tm_mon, lt().tm_mday)

def login(username, password):
	session = requests.Session()
	session.headers['User-Agent'] = configs.browser_version
	session.post(
		urls.url_login,
		data={'Account': username, 'Password': password})
	return session

def login_asset(session, password):
	response = session.post(
		urls.url_login_asset, data={'value': password})
	errmsg = eval(response.content)['FAIL']
	if errmsg is not '':
		print (errmsg, file=sys.stderr)
		return False
	else:
		return True

def get_case_stats(
	session, exec_y=None, exec_t=None, exec_n1=None, exec_n2=None,
	uid='', dept='', noendbox=True, YNK=True, summary=False):
	all_cases = []
	all_stats = None
	if exec_n1 is None and exec_n2 is not None:
		exec_n1 = exec_n2
	if exec_n2 is None and exec_n1 is not None:
		exec_n2 = exec_n1
	if exec_n1 is not None and exec_n2 - exec_n1 >= 2000:
		if summary is True:
			all_cases, all_stats = get_case_stats(
				session, exec_y, exec_t, exec_n1, exec_n2 - 2000,
				uid, dept, noendbox, YNK, summary)
		else:
			all_cases = get_case_stats(
				session, exec_y, exec_t, exec_n1, exec_n2 - 2000,
				uid, dept, noendbox, YNK, summary)
		exec_n1 = exec_n2 - 2000 + 1
	data = {
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S]': formatted('%08d', exec_n1),
		'model[EXEC_SEQNO_E]': formatted('%08d', exec_n2),
		'model[DEPT_NO]': dept,
		'model[DUTY_IDNO]': uid.strip(),
		'model[ORDERBY]': 1,
		'model[KEY_IN_RECEIVE]': str(YNK).lower(),
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size
	}
	if noendbox is True:
		data['model[NOENDBOX][]'] = 'NOENDBOX'
	current_useless_attrs = [
		'model[EXEC_NO_TEXT]', 'model[DIST_DATE_S]', 'model[DIST_DATE_E]',
		'model[END_DATE_S]', 'model[END_DATE_E]', 'model[PAY_DATE_S]',
		'model[PAY_DATE_E]', 'model[STOP_DATE]', 'model[SEND_CLASS_ID_S]',
		'model[SEND_CLASS_ID_E]', 'model[BATCH_YEAR]', 'model[BATCH_NO]',
		'model[SEND_ORG_ID]', 'model[DUTY_NAME]', 'model[LEGAL_IDNO]',
		'model[LEGAL_NAME]', 'model[MANAGE_ID]', 'model[CONTROL_TYPE]',
		'model[ATTR_ID]', 'model[END_SITU]', 'model[SENDBOX]',
		'model[ALLDUTYBOX]', 'model[PRE_PAY_DATE]',
		'model[paginaiton][totalCount]']
	for attr in current_useless_attrs:
		data[attr] = ''
	raw_response = session.post(urls.url_case_stats, data=data)
	response = eval(regulized(raw_response.text))
	partial_cases = response['gridDatas']
	key_info = [
		'EXEC_YEAR', 'EXEC_CASE', 'EXEC_SEQNO', 'DEPT_NO', 'DUTY_IDNO',
		'DUTY_NAME', 'MAIN_EXEC_NO', 'END_DATE', 'FINISH_DATE', 'SEND_ORG_ID',
		'PAY_AMT', 'RECEIVE_AMT', 'RETURN_AMT', 'RETURN_AMT_NO', 'EVI_AMT',
		'END_SITU_NAME', 'KEY_IN_RECEIVE', 'KEY_IN_RETURN', 'RECEIVE_FLAG']
	partial_cases = [
		{info: case[info] for info in key_info} for case in partial_cases]
	all_cases += partial_cases
	if summary is True:
		partial_stats = response['QueryTotal_AMT'][0]
		for key, value in partial_stats.items():
			partial_stats[key] = int(value.replace(',', ''))
		if all_stats is None:
			all_stats = partial_stats
		else:
			for key, value in partial_stats.items():
				all_stats[key] += value
		return all_cases, all_stats
	else:
		return all_cases

def get_asset_page(
	session, password, uid,
	date_begin=configs.asset_date_begin, date_end='%03d%02d%02d' % today()):
	if login_asset(session, password) is False:
		return []
	data = {
		'model[PKNO]': '',
		'model[DUTY_IDNO_TEXTAREA]': uid,
		'model[IMP_DATE_BEGIN]': date_begin,
		'model[IMP_DATE_END]': date_end,
		'model[INCLUDE_SELF_ADDED_CHECK_BOX]': '',
		'model[IMP_RESULT]': 0,
		'model[EXEC_YEAR]': '',
		'model[EXEC_CASE]': '',
		'model[EXEC_SEQNO_S]': '',
		'model[EXEC_SEQNO_E]': '',
		'model[PRINTTYPE]': '',
		'model[paginaiton][pages][]': 1,
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size,
		'model[paginaiton][totalPage]': '',
		'model[paginaiton][totalCount]': ''
	}
	response = session.post(urls.url_asset, data=data)
	return eval(response.content)['gridDatas']

def download_asset_page(
	session, password, uid,
	date_begin=configs.asset_date_begin, date_end='%03d%02d%02d' % today(),
	file_path=configs.default_asset_page_path):
	if login_asset(session, password) is False:
		return False
	data = {
		'PKNO': '',
		'DUTY_IDNO_TEXTAREA': uid,
		'IMP_DATE_BEGIN': date_begin,
		'IMP_DATE_END': date_end,
		'INCLUDE_SELF_ADDED_CHECK_BOX': '',
		'IMP_RESULT': 0,
		'EXEC_YEAR': '',
		'EXEC_CASE': '',
		'EXEC_SEQNO_S': '',
		'EXEC_SEQNO_E': '',
		'PRINTTYPE': ''
	}
	response = session.post(urls.url_asset_print, data=data)
	with open(file_path, 'wb') as f:
		f.write(response.content)
	return True

def get_old_ended_cases_stats(
	session, exec_y=None, ended_y=None, exec_t=None, exec_n1=None, exec_n2=None,
	in_date_s=None, in_date_e=None, dept='', keepterm=None):
	"""
	This function is only available for file manager account.
	For those cases ended before 98y, all cases share a number
	series regardless of their type, but still stored separately.
	Besides, the series number has form as
		%03d-CY-%03d%02d%08d %
			(exec_y, ended_y, case_type, series_number)
	And current system doesn't support to leave exec_y to be empty.
	That is to say, if anyone want to get cases ended in some year,
	he/she has to send lots of queries which fully cover all possible
	exec_y by him/herself.
	"""
	if case_n2 is None:
		case_n2 = case_n1
	voc_group = [exec_y, ended_y, exec_t, exec_n1, exec_n2]
	count_none = sum([1 if ele is None else 0 for ele in voc_group])
	if count_none == len(voc_group):
		voc_type = 0
	elif count_none == 0:
		voc_type = 1
	else:
		print ('請確認下列資料是否齊全: 執行年度、歸檔年度、案件別、檔號',
			file=sys.stderr)
		raise ValueError
	data = {
		'model[EXEC_YEAR]': '',
		'model[EXEC_CASE]': '',
		'model[EXEC_SEQNO]': '',
		'model[EXEC_SEQNO_S]': '',
		'model[EXEC_SEQNO_E]': '',
		'model[END_FILE_NO]': '',
		'model[EXEC_RECTYPE]': '',
		'model[VOC_YEAR]': formatted('%03d', exec_y),
		'model[VOC_TYPE_SNAME]': 'CY',
		'model[VOC_SEQ_YEAR1]': formatted('%03d', ended_y),
		'model[VOC_CASE_TYPE1]': formatted('%02d', exec_t),
		'model[VOC_SEQ_NO_S1]': formatted('%08d', exec_n1),
		'model[VOC_SEQ_NO_E1]': formatted('%08d', exec_n2),
		'model[VOC_SEQ_YEAR2]': '',
		'model[VOC_CASE_TYPE2]': '',
		'model[VOC_SEQ_NO_S2]': '',
		'model[VOC_SEQ_NO_E2]': '',
		'model[VOC_TYPE]': voc_type,
		'model[QRY_TYPE]': '',
		'model[FILE_KIND]': '',
		'model[DUTY_IDNO]': '',
		'model[DUTY_NAME]': '',
		'model[END_FILE_DATE_S]': formatted('%03d%02d%02d', in_date_s),
		'model[END_FILE_DATE_E]': formatted('%03d%02d%02d', in_date_e),
		'model[DEPT_NO]': dept,
		'model[CASE_TYPE]': '',
		'model[END_SITU]': '',
		'model[KEEPTERM]': formatted('%03d', keepterm),
		'model[ORDERBY]': '',
		'model[USER_NO]': '',
		'model[paginaiton][pages][]': 1,
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size,
		'model[paginaiton][totalPage]': '',
		'model[paginaiton][totalCount]': ''
	}
	response = session.post(urls.url_ended_case_stats, data=data)
	return eval(response.content)['gridDatas']

def ending_cases(
	session, dept, exec_y, exec_t, exec_n, end_situ=None,
	end_y=today()[0], end_m=today()[1], end_d=today()[2],
	evi_amt=None, undo=False):
	# Stage 1: get cases attributes
	data = {
		'model[PKNO]': '',
		'model[CASE_KIND]': 1,
		'model[QTYPE]': 1,
		'model[EXEC_YEAR_M]': formatted('%03d', exec_y),
		'model[EXEC_CASE_M]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S_M]': formatted('%08d', exec_n),
		'model[EXEC_SEQNO_E_M]': formatted('%08d', exec_n),
		'model[CHECK_STATUS]': 'false',
		'model[OUT_DATE_S]': '',
		'model[OUT_DATE_E]': '',
		'model[MTYPE]': 1,
		'model[ETYPE]': 1 if undo is False else 2,
		'model[END_DATE]': '',
		'model[DEPT_NO]': dept,
		'model[END_DATE_SET]': '%03d%02d%02d' % today(),
		'model[DUTY_IDNO]': '',
		'model[EXEC_YEAR_S]': '',
		'model[EXEC_CASE_S]': '',
		'model[EXEC_SEQNO_S]': '',
		'model[EXEC_SEQNO_S_E]': '',
		'model[END_SITU_ID]': '',
		'model[CASE_KIND_B]': 1,
		'model[END_DATE_B]': '%03d%02d%02d' % today(),
		'model[QTYPE_B]': 1,
		'model[EXEC_YEAR_B_M]': '', 
		'model[EXEC_CASE_B_M]': '',
		'model[EXEC_SEQNO_S_B_M]': '',
		'model[EXEC_SEQNO_E_B_M]': '',
		'model[ETYPE_B]': 1,
		'model[EXEC_YEAR_B_S]': '',
		'model[EXEC_CASE_B_S]': '',
		'model[EXEC_SEQNO_B_S]': '',
		'model[SET_END_SITU_ID_B]': '',
		'model[SET_END_SITU_ID_B_S]': '',
		'model[CONTROL_TYPE]': '', 
		'model[CLASS_ID]': '',
		'model[ATTR_ID]': '',
		'model[QTYPE_2]': '',
		'model[ORDERBY]': '',
		'model[ORDERBY_B]': ''
	}
	response = session.post(urls.url_cases_attributes, data=data)
	try:
		attr = eval(regulized(response.text))['gridDatas'][0]
	except:
		return False, '查無案件資料'
	"""
	Stage 2: post requests
		Both 2-1(do) and 2-2(undo) will inherit most attributes from case
		attributes, so those customized attributes will be added into attr
		to make it consistent.
	"""
	# Stage 2-1: post ending request
	if undo is False:
		if end_situ is None and attr['END_SITU_ID'] == '':
			return False, '請提供終結情形'
		inherited_key_words = [
			'PKNO', 'EXEC_YEAR', 'EXEC_CASE', 'EXEC_SEQNO',
			'END_SITU_ID_SP', 'END_SITU_ID_BASE', 'EXEC_NO',
			'DUTY_IDNO', 'LEGAL_IDNO', 'DEPT_NO', 'SEND_ORG_ID',
			'PAY_AMT', 'RECEIVE_AMT', 'RETURN_AMT', 'UNDO_AMT',
			'UN_RETURN_AMT']
		customized_key_words = [
			'END_SITU_ID', 'DEPT_NO', 'END_DATE_SET', 'EVI_AMT',
			'END_SITU_ID_BOOL', 'QTYPE_2', 'ORDERBY', 'ORDERBY_B']
		customized_key_values = [
			end_situ if end_situ is not None else int(attr['END_SITU_ID']),
			dept, (end_y, end_m, end_d),
			evi_amt if evi_amt is not None else int(attr['UNDO_AMT']),
			'false', None, None, None]
		customized_key_formats = [
			"%02d", "%s", "%03d%02d%02d", "%d", "%s", '', '', '']
		zipper = zip(
			customized_key_words,
			customized_key_values,
			customized_key_formats)
		for key, value, format_str in zipper:
			attr[key] = formatted(format_str, value)
	# Stage 2-2: post undo-ending request
	else:
		inherited_key_words = [
			'PKNO', 'EXEC_YEAR', 'EXEC_CASE', 'EXEC_SEQNO', 'END_SITU_ID',
			'END_SITU_ID_SP' , 'END_SITU_ID_BASE', 'EXEC_NO', 'UNDO_AMT']
		customized_key_words = []
		customized_key_values = []
		customized_key_formats = []
	data = {
		('model[0][%s]' % word): attr[word]
		for word in inherited_key_words + customized_key_words}
	url = [urls.url_cancel_ended_request, urls.url_post_ended_request]
	response = session.post(
		url[0 if undo is True else 1], data=data)
	success_msg = eval(response.text)['SUCCESS']
	fail_msg = eval(response.text)['FAIL']
	if fail_msg is not '':
		return False, fail_msg
	elif '失敗' in success_msg:
		fail_msg = success_msg.split('，')[-1].split('\n')[-2]
		return False, fail_msg
	else:
		success_msg = success_msg.split('\n')[-2]
		return True, success_msg

def get_topay_summary(
	session, exec_y=None, exec_t=None, exec_n=None, uid=None):
	data = {
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S]': formatted('%08d', exec_n),
		'model[EXEC_SEQNO_E]': formatted('%08d', exec_n),
		'model[DUTY_IDNO]': formatted('%s', uid),
		'model[CLASS_ID_A]': '',
		'model[DEPT_NO]': '',
		'model[SEND_ORG_ID_S]': '',
		'model[SEND_ORG_ID_E]': '',
		'model[PRE_PAY_DATE]': '%03d%02d%02d' % today(),
		'model[SUB_TYPE]': 1,
		'model[DATA_TYPE]': 1,
		'model[IS_RECEIVE_FLAG]': '',
		'model[IS_NO_ZERO]': '',
		'model[CONTROL_TYPE]': '',
		'model[ATTR_ID]': ''
	}
	response = session.post(urls.url_topay_summary, data=data)
	return int(eval(response.text)['gridDatas'][-1]['TOT_AMT'])

if __name__ == '__main__':
	"""Preserved for unit-test only."""