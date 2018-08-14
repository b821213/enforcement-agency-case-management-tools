import requests
import sys
import urls
import configs
from time import localtime as lt
from share_lib import formatted

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
	if len(session.cookies) == 0:
		return None
	else:
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

def get_default_dept_list(session):
	url = urls.url_home_page
	response = session.post(url)
	return eval(regulized(response.text))['DEPT_NO_LIST']

def get_complete_dept_list(session):
	# Currently only accessible to file manager accounts.
	url = urls.url_file_option_list
	response = session.post(url)
	complete_dept_list = [
		pair['value'] for pair in eval(response.text)['DEPT_NO']
		if pair['value'] != '']
	return complete_dept_list

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
		'model[paginaiton][totalCount]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	raw_response = session.post(urls.url_case_stats, data=data)
	response = eval(regulized(raw_response.text))
	partial_cases = response['gridDatas']
	key_info_str = [
		'MAIN_EXEC_NO', 'DEPT_NO', 'DUTY_IDNO', 'DUTY_NAME',
		'SEND_ORG_ID', 'SEND_ORG_NAME', 'END_DATE', 'FINISH_DATE',
		'END_SITU_NAME', 'KEY_IN_RECEIVE', 'KEY_IN_RETURN', 'RECEIVE_FLAG'
	]
	key_info_int = [
		'EXEC_YEAR', 'EXEC_CASE', 'EXEC_SEQNO', 'PAY_AMT', 'RECEIVE_AMT',
		'RETURN_AMT', 'RETURN_AMT_NO', 'EVI_AMT'
	]
	to_integer = lambda s: int(s.replace(',', ''))
	partial_cases = [{
		**{info: case[info] for info in key_info_str},
		**{info: to_integer(case[info]) for info in key_info_int}}
		for case in partial_cases]
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
	if type(uid) is list:
		uid_str = '\n'.join(uid)
	else:
		uid_str = uid
	data = {
		'model[DUTY_IDNO_TEXTAREA]': uid_str,
		'model[IMP_DATE_BEGIN]': date_begin,
		'model[IMP_DATE_END]': date_end,
		'model[IMP_RESULT]': 0,
		'model[paginaiton][pages][]': 1,
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size
	}
	current_useless_attrs = [
		'model[PKNO]', 'model[INCLUDE_SELF_ADDED_CHECK_BOX]',
		'model[EXEC_YEAR]', 'model[EXEC_CASE]', 'model[EXEC_SEQNO_S]',
		'model[EXEC_SEQNO_E]', 'model[PRINTTYPE]',
		'model[paginaiton][totalPage]', 'model[paginaiton][totalCount]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_asset, data=data)
	return eval(response.content)['gridDatas']

def download_asset_page(
	session, password, uid,
	date_begin=configs.asset_date_begin, date_end='%03d%02d%02d' % today(),
	file_path=configs.default_asset_page_path):
	if login_asset(session, password) is False:
		return False
	if type(uid) is list:
		uid_str = '\n'.join(uid)
	else:
		uid_str = uid
	data = {
		'DUTY_IDNO_TEXTAREA': uid_str,
		'IMP_DATE_BEGIN': date_begin,
		'IMP_DATE_END': date_end,
		'IMP_RESULT': 0
	}
	current_useless_attrs = [
		'PKNO', 'INCLUDE_SELF_ADDED_CHECK_BOX', 'EXEC_YEAR', 'EXEC_CASE',
		'EXEC_SEQNO_S', 'EXEC_SEQNO_E', 'PRINTTYPE'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_asset_print, data=data)
	if '<script>' in response.text:
		# This is the head of the error message.
		return False
	with open(file_path, 'wb') as f:
		f.write(response.content)
	return True

def get_todestroy_case_stats(
	session, todo_date_s=None, todo_date_e=None,
	ended_date_s=None, ended_date_e=None, dept='', keepterm='',
	exec_y=None, exec_t=None, exec_n1=None, exec_n2=None,
	a98_end_code=None):
	if exec_n2 is None:
		exec_n2 = exec_n1
	data = {
		'model[QUERY_TYPE]': 'N',
		'model[DEPT_NO]': dept,
		'model[KEEPTERM]': keepterm,
		'model[REC_TYPE]': 'A',
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S]': formatted('%08d', exec_n1),
		'model[EXEC_SEQNO_E]': formatted('%08d', exec_n2),
		'model[END_FILE_DATE_S]': formatted('%03d%02d%02d', ended_date_s),
		'model[END_FILE_DATE_E]': formatted('%03d%02d%02d', ended_date_e),
		'model[SHOULD_DESTORY_DATE_S]': formatted('%03d%02d%02d', todo_date_s),
		'model[SHOULD_DESTORY_DATE_E]': formatted('%03d%02d%02d', todo_date_e),
		'model[FILEKIND]': formatted('%08d', a98_end_code),
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size
	}
	current_useless_attrs = [
		'model[DUTY_NAME]', 'model[EXEC_CASE_B]', 'model[FILESTATUS]',
		'model[YEAR_TYPE]', 'model[YEAR98B_CASE]', 'model[YEAR98A_FILEKIND]',
		'model[DESTROY_YEAR]', 'model[DESTROY_BATNO]',
		'model[SHOULD_DESTORY_NUM]', 'model[SHOULD_DESTORY_CASE_NUM]',
		'model[paginaiton][totalCount]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_todestroy_case_stats, data=data)
	return eval(response.content)['gridDatas']

def get_ended_case_stats(
	session, in_date_s=None, in_date_e=None, dept='',
	b98_exec_y=None, b98_ended_y=None, b98_exec_t=None, b98_exec_n1=None,
	b98_exec_n2=None, a98_end_code=None, a98_exec_t=None, a98_ended_y=None,
	a98_exec_n1=None, a98_exec_n2=None,
	exec_y=None, exec_t=None, exec_n1=None, exec_n2=None,
	uid='', end_situ=None, keepterm=''):
	"""
	For those cases ended before 98y, all cases share a number
	series regardless of their type, but still stored separately.
	Besides, the series number has form as
		%03d-CY-%03d%02d%08d %
			(b98_exec_y, b98_ended_y, case_type, series_number)

	Notice that exec_t should be [AB]%02d.
	"""
	if b98_exec_n2 is None:
		b98_exec_n2 = b98_exec_n1
	b98_attrs = [b98_exec_y, b98_ended_y, b98_exec_t, b98_exec_n1, b98_exec_n2]
	b98_count_none = sum([1 if attr is None else 0 for attr in b98_attrs])
	if a98_exec_n2 is None:
		a98_exec_n2 = a98_exec_n1
	a98_attrs = [
		a98_end_code, a98_exec_t, a98_ended_y, a98_exec_n1, a98_exec_n2]
	a98_count = sum([0 if attr is None else 1 for attr in a98_attrs])
	if b98_count_none == 0 and a98_count > 0:
		raise ValueError('請確認查詢標的為 98 年前案件或 98 年後案件')
	elif b98_count_none == 0:
		voc_type = 1
	elif a98_count > 0:
		voc_type = 2
	elif b98_count_none != len(b98_attrs):
		raise ValueError(
				'請確認下列資料是否齊全: 執行年度、歸檔年度、案件別、檔號')
	else:
		voc_type = 0
	data = {
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%s', exec_t),
		'model[EXEC_SEQNO_S]': formatted('%08d', exec_n1),
		'model[EXEC_SEQNO_E]': formatted('%08d', exec_n2),
		'model[VOC_YEAR]': formatted('%03d', b98_exec_y),
		'model[VOC_TYPE_SNAME]': 'CY',
		'model[VOC_SEQ_YEAR1]': formatted('%03d', b98_ended_y),
		'model[VOC_CASE_TYPE1]': formatted('%02d', b98_exec_t),
		'model[VOC_SEQ_NO_S1]': formatted('%08d', b98_exec_n1),
		'model[VOC_SEQ_NO_E1]': formatted('%08d', b98_exec_n2),
		'model[FILE_KIND]': formatted('%08d', a98_end_code),
		'model[VOC_CASE_TYPE2]': formatted('%02d', a98_exec_t),
		'model[VOC_SEQ_YEAR2]': formatted('%03d', a98_ended_y),
		'model[VOC_SEQ_NO_S2]': formatted('%07d', a98_exec_n1),
		'model[VOC_SEQ_NO_E2]': formatted('%07d', a98_exec_n2),
		'model[VOC_TYPE]': voc_type,
		'model[END_FILE_DATE_S]': formatted('%03d%02d%02d', in_date_s),
		'model[END_FILE_DATE_E]': formatted('%03d%02d%02d', in_date_e),
		'model[DEPT_NO]': dept,
		'model[DUTY_IDNO]': uid,
		'model[END_SITU]': formatted('%02d', end_situ),
		'model[KEEPTERM]': keepterm,
		'model[paginaiton][pages][]': 1,
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size
	}
	current_useless_attrs = [
		'model[EXEC_SEQNO]', 'model[END_FILE_NO]', 'model[EXEC_RECTYPE]',
		'model[QRY_TYPE]', 'model[DUTY_NAME]', 'model[CASE_TYPE]',
		'model[ORDERBY]', 'model[paginaiton][totalPage]', 
		'model[paginaiton][totalCount]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_ended_case_stats, data=data)
	return eval(response.content)['gridDatas']

def ending_cases(
	session, dept, exec_y, exec_t, exec_n, end_situ=None,
	end_y=today()[0], end_m=today()[1], end_d=today()[2],
	evi_amt=None, undo=False):
	# Stage 1: get cases attributes
	data = {
		'model[CASE_KIND]': 1,
		'model[QTYPE]': 1,
		'model[EXEC_YEAR_M]': formatted('%03d', exec_y),
		'model[EXEC_CASE_M]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S_M]': formatted('%08d', exec_n),
		'model[EXEC_SEQNO_E_M]': formatted('%08d', exec_n),
		'model[CHECK_STATUS]': 'false',
		'model[MTYPE]': 1,
		'model[ETYPE]': 1 if undo is False else 2,
		'model[DEPT_NO]': dept,
		'model[END_DATE_SET]': '%03d%02d%02d' % today(),
		'model[CASE_KIND_B]': 1,
		'model[END_DATE_B]': '%03d%02d%02d' % today(),
		'model[QTYPE_B]': 1,
		'model[ETYPE_B]': 1,
	}
	current_useless_attrs = [
		'model[PKNO]', 'model[OUT_DATE_S]', 'model[OUT_DATE_E]',
		'model[END_DATE]', 'model[DUTY_IDNO]', 'model[EXEC_YEAR_S]',
		'model[EXEC_CASE_S]', 'model[EXEC_SEQNO_S]', 'model[EXEC_SEQNO_S_E]',
		'model[END_SITU_ID]', 'model[EXEC_YEAR_B_M]', 'model[EXEC_CASE_B_M]',
		'model[EXEC_SEQNO_S_B_M]', 'model[EXEC_SEQNO_E_B_M]',
		'model[EXEC_YEAR_B_S]', 'model[EXEC_CASE_B_S]', 'model[EXEC_SEQNO_B_S]',
		'model[SET_END_SITU_ID_B]', 'model[SET_END_SITU_ID_B_S]',
		'model[CONTROL_TYPE]', 'model[CLASS_ID]', 'model[ATTR_ID]',
		'model[QTYPE_2]', 'model[ORDERBY]', 'model[ORDERBY_B]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
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
		situ_with_evi = [4, 5, 12, 15, 90, 91, 94, 96]
		inherited_key_words = [
			'PKNO', 'EXEC_YEAR', 'EXEC_CASE', 'EXEC_SEQNO',
			'END_SITU_ID_SP', 'END_SITU_ID_BASE', 'EXEC_NO',
			'DUTY_IDNO', 'LEGAL_IDNO', 'DEPT_NO', 'SEND_ORG_ID',
			'PAY_AMT', 'RECEIVE_AMT', 'RETURN_AMT', 'UNDO_AMT',
			'UN_RETURN_AMT']
		customized_key_words = [
			'END_SITU_ID', 'DEPT_NO', 'END_DATE_SET', 'EVI_AMT',
			'END_SITU_ID_BOOL', 'QTYPE_2', 'ORDERBY', 'ORDERBY_B']
		if end_situ is None:
			end_situ = int(attr['END_SITU_ID'])
		if evi_amt is None:
			evi_amt = (
				max(int(attr['UNDO_AMT']), 1) if end_situ in situ_with_evi
				else 0)
		customized_key_values = [
			end_situ, dept, (end_y, end_m, end_d), evi_amt,
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
	session, exec_y=None, exec_t=None, exec_n1=None, exec_n2=None, uid=''):
	if exec_n1 is None:
		exec_n1 = exec_n2
	if exec_n2 is None:
		exec_n2 = exec_n1
	data = {
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_S]': formatted('%08d', exec_n1),
		'model[EXEC_SEQNO_E]': formatted('%08d', exec_n2),
		'model[DUTY_IDNO]': formatted('%s', uid),
		'model[PRE_PAY_DATE]': '%03d%02d%02d' % today(),
		'model[SUB_TYPE]': 1,
		'model[DATA_TYPE]': 2
	}
	current_useless_attrs = [
		'model[CLASS_ID_A]', 'model[DEPT_NO]', 'model[SEND_ORG_ID_S]',
		'model[SEND_ORG_ID_E]', 'model[IS_RECEIVE_FLAG]', 'model[IS_NO_ZERO]',
		'model[CONTROL_TYPE]', 'model[ATTR_ID]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_topay_summary, data=data)
	return int(eval(response.text)['gridDatas'][-1]['TOT_AMT'])

def get_detainable_list(session, dept):
	data = {
		'model[DEPT_NO]': dept,
		'model[paginaiton][pageNo]': 1,
		'model[paginaiton][pageSize]': configs.default_page_size,
	}
	current_useless_attrs = [
		'model[paginaiton][totalPage]', 'model[paginaiton][totalCount]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_detainable_list, data=data)
	return eval(response.text)['gridDatas']

def get_case_details(session, exec_y=None, exec_t=None, exec_n=None, uid=''):
	data = {
		'model[EXEC_YEAR_Q]': formatted('%03d', exec_y),
		'model[EXEC_CASE_Q]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO_Q]': formatted('%08d', exec_n),
		'model[DUTY_IDNO_Q]': formatted('%s', uid)
	}
	current_useless_attrs = ['model[DUTY_NAME_Q]']
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_case_details, data=data)
	raw = eval(response.text)
	if raw['FAIL'] != '':
		return None
	key_info = ['EXEC_DATE', 'REMARK', 'EXEC_MRK']
	return {
		'DUTY_NAME': raw['DUTY_NAME'],
		'DUTY_IDNO': raw['DUTY_IDNO_ALL'].split(','),
		'SITU_LIST': [
			{key: situ[key] for key in key_info} for situ in raw['SITU_LIST']],
		'IS_WHOLLY_OWNED': raw['INV'] == '1',
		'IS_PARTNERSHIP': raw['INV'] == '2',
		'BEGIN_DATE': (
			None if raw['ADM_DATE'] == ''
			else tuple(map(int, raw['ADM_DATE'].split('/'))))
	}

def download_bank_response(
	session, exec_y=None, exec_t=None, exec_n=None,
	send_date_s=None, send_date_e=None,
	receive_date_s=None, receive_date_e=None,
	show_hi=True, show_li=True, dept='', uid='',
	file_path=configs.default_bank_response_path):
	if show_hi is True and show_li is True:
		data_type = ''
	elif show_hi is False and show_li is False:
		data_type = 1
	elif show_hi is True and show_li is False:
		data_type = 2
	else:
		data_type = 3
	data = {
		'model[DUTY_IDNO]': uid,
		'model[EXEC_YEAR]': formatted('%03d', exec_y),
		'model[EXEC_CASE]': formatted('%02d', exec_t),
		'model[EXEC_SEQNO]': formatted('%08d', exec_n),
		'model[OUTDATE_S]': formatted('%03d%02d%02d', send_date_s),
		'model[OUTDATE_E]': formatted('%03d%02d%02d', send_date_e),
		'model[RECEIVE_DATE_S]': formatted('%03d%02d%02d', receive_date_s),
		'model[RECEIVE_DATE_E]': formatted('%03d%02d%02d', receive_date_e),
		'model[DATA_TYPE]': data_type,
		'model[DEPT_NO]': dept,
	}
	current_useless_attrs = [
		'model[DETAIN_TYPE]', 'model[REPLY_TYPE]', 'model[ATTR_ID]',
		'model[CONTROL_TYPE]', 'model[ISSUE_NO]'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_bank_response_print, data=data)
	if '<script>' in response.text:
		# This is the head of the error message.
		return False
	with open(file_path, 'wb') as f:
		f.write(response.content)
	return True

def download_payment_list(
	session, date_s=None, date_e=None,
	exec_y=None, exec_t=None, exec_n1=None, exec_n2=None,
	money_lb=None, money_ub=None, dept='', uid='',
	show_key_in=True, show_electronic=True,
	show_normal=True, show_hi=True, show_li=True,
	file_path=configs.default_payment_list_path):
	k_filter_map = {
		(True, True): '',
		(True, False): 1,
		(False, True): 2
	}
	i_filter_map = {
		(True, True, True): '',
		(True, False, True): 1,
		(True, True, False): 2,
		(False, True, False): 3,
		(False, False, True): 4,
		(True, False, False): 5,
		(False, True, True): 6
	}
	if show_key_in is False and show_electronic is False:
		return False
	if show_normal is False and show_hi is False and show_li is False:
		return False
	data = {
		'YMD_S': formatted('%03d%02d%02d', date_s),
		'YMD_E': formatted('%03d%02d%02d', date_e),
		'EXEC_YEAR': formatted('%03d', exec_y),
		'EXEC_CASE': formatted('%02d', exec_t),
		'EXEC_SEQNO_S': formatted('%08d', exec_n1),
		'EXEC_SEQNO_E': formatted('%08d', exec_n2),
		'PAY_AMT_S': formatted('%d', money_lb),
		'PAY_AMT_E': formatted('%d', money_ub),
		'DEPT_NO': dept,
		'DUTY_IDNO': uid,
		'QTYPE': k_filter_map[(show_key_in, show_electronic)],
		'QTYPE_2': i_filter_map[(show_normal, show_hi, show_li)],
		'STYPE': 1,
		'STYPE_2': 1
	}
	current_useless_attrs = [
		'PKNO', 'SEND_ORG_ID', 'DUTY_NAME', 'CLASS_ID', 'TIMES', 'EXEC_DEPT_ID',
		'Q_YM', 'CONDITION_1', 'CONDITION_2', 'CONDITION_3', 'CONDITION_4'
	]
	for attr in current_useless_attrs:
		data[attr] = ''
	response = session.post(urls.url_payment_list_print, data=data)
	if '<script>' in response.text:
		# This is the head of the error message.
		return False
	with open(file_path, 'wb') as f:
		f.write(response.content)
	return True

if __name__ == '__main__':
	"""Preserved for unit-test only."""
