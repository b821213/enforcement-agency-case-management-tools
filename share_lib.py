import sys
import re

def formatted(form, value):
	"""This function is only used for simplifying code."""
	return '' if value is None else form % value

def read_input(file_path):
	f = open(file_path, 'r')
	ret = []
	for line in f:
		data = line[:-1].split(',')
		if len(data) < 3:
			uid = data[0]
			if len(data) == 1 or data[1] is not '':
				ret.append(uid)
		else:
			y, t, n = map(int, data[:3])
			if len(data) == 3 or data[3] is not '':
				ret.append((y, t, n))
	f.close()
	return ret

def print_and_record(*args, **kargs):
	print (*args)
	print (*args, **kargs)

def is_hi_case(case):
	return case['EXEC_CASE'] == 2

def is_li_case(case):
	return case['SEND_ORG_ID'] == '107001'

def ranged_case_list(session, case_list):
	"""
	Input: type(get_case_stats(...))
	Output: a list of (y, t, n1, n2, note1, note2)
	If note1 == '*': it is health/labor insurance.
	If note2 == '#': it can be ended, i.e. to-pay amount is zero.
	"""
	# A case is described as (y, t, n, is_hi, is_li).
	cur_last = (-1, -1, -1, False, False)
	cur_left = (-1, -1, -1, False, False)
	all_clear = True
	ret_list = []
	for case in case_list:
		y = int(case['EXEC_YEAR'])
		t = int(case['EXEC_CASE'])
		n = int(case['EXEC_SEQNO'])
		is_hi = is_hi_case(case)
		is_li = is_li_case(case)
		is_clear = get_topay_single(session, case) == 0
		if (y != cur_last[0] or t != cur_last[1] or n != cur_last[2] + 1 or
			is_hi != cur_last[3] or is_li != cur_last[4]):
			note1 = '#' if all_clear is True else ''
			note2 = '*' if any(cur_last[-2:]) is True else ''
			ret_list.append((*cur_left[:3], cur_last[2], note1, note2))
			all_clear = True
			cur_left = (y, t, n, is_hi, is_li)
		if is_clear is False:
			all_clear = False
		cur_last = (y, t, n, is_hi, is_li)
	note1 = '#' if all_clear is True else ''
	note2 = '*' if any(cur_last[-2:]) is True else ''
	ret_list.append((*cur_left[:3], cur_last[2], note1, note2))
	return ret_list[1:]

def print_for_merge(ranged_cl, f_out=sys.stdout):
	data = sorted(ranged_cl, key=lambda x: (x[1], x[0], x[2]))
	to_print = []
	for ranged_n in data:
		if ranged_n[2] == ranged_n[3]:
			to_print.append('%03d-%02d-%06d%7s%1s%1s' %
				(*ranged_n[:3], '', *ranged_n[-2:]))
		else:
			to_print.append('%03d-%02d-%06d~%06d%1s%1s' % ranged_n)
	to_print_in_row = []
	for i in range(0, len(to_print), 5):
		to_print_in_row.append(
			'\t' + '\t'.join(to_print[i : i + 5]))
	print ('\n'.join(to_print_in_row), file=f_out)

re_mainno = re.compile(r'\(代表號\d{3}-\d{2}-\d{8}\)')
re_callpay = re.compile(r'\d*/\d*/\d*應到')
re_lookinto = re.compile(r'調查\(.*\)')
re_output = re.compile(r'匯出')
re_e_mainno = re.compile(r'發文字號.{3}\d{3}.\d{8}字')
re_e_docno = re.compile(r'嘉執.\d{3}.\d{8}字第\d{10}[A-Z]號')
re_e_done = re.compile(r'已電子公文交換')
re_e_response = re.compile(r'已扣押.*及手續費')
re_three_sheet = re.compile(r'案款收領款繳款暨發\(還\)款通知')
re_launch = re.compile(r'發出文件.*')

def refined_command(raw_command):
	# rule-based refinements
	command = raw_command
	comment = ''
	main_num = ''
	# get main seqno
	m = re_mainno.search(command)
	if m is not None:
		main_num = command[m.start() + 4: m.end() - 1]
		command = command[: m.start()] + command[m.end():]
	# the following conditions should be mutual exclusive
	# notice that the order is important
	m = re_callpay.search(command)
	if m is not None:
		y, m, d = map(int, command[m.start(): m.end() - 2].split('/'))
		y -= 1911
		command = '傳繳 (%03d/%02d/%02d 止)' % (y, m, d)
	m = re_lookinto.search(command)
	if m is not None:
		comment = command[m.start() + 3: m.end() - 1].split(',')
		command = '調查個人資料'
	m = re_output.search(command)
	if m is not None:
		comment = command[: m.end() - 2]
		command = '資料匯出'
	m = re_e_mainno.search(command)
	if m is not None:
		t_map = {'稅': 1, '健': 2, '罰': 3, '費': 4}
		y = int(command[m.start() + 7: m.start() + 10])
		t = t_map[command[m.start() + 10]]
		n = int(command[m.start() + 11: m.start() + 19])
		main_num = '%03d-%02d-%08d' % (y, t, n)
		m = re_e_docno.search(command)
		if m is not None:
			comment = command[m.start(): m.end()]
		command = command.split(',')[0]
	m = re_e_response.search(command)
	if m is not None:
		comment = command[: m.start()]
		command = '金融機構回覆'
	m = re_three_sheet.search(command)
	if m is not None:
		comment = re.search(r'\d+', command).group()
		command = '三聯單'
	m = re_launch.search(command)
	if m is not None:
		command = command[m.start() + 4: m.end()]
	return command, comment, main_num

def refined_situ_list(situ_list):
	tmp_list = []
	for situ in situ_list:
		y, m, d = map(int, situ['EXEC_DATE'].split()[0].split('/'))
		y -= 1911
		date = (y, m, d)
		command, comment, main_num = refined_command(situ['REMARK'])
		if command == '':
			command = '執行終結'
		tmp_list.append((date, command, comment, main_num))
	ret_list = []
	docno_map = {}
	for date, command, comment, main_num in tmp_list:
		if command in {'資料匯出', '收發註記已發', '金融機構回覆'}:
			continue
		# here use str(comment) since comment may be a list
		if re_e_docno.match(str(comment)) is not None:
			date_list = docno_map.get(comment)
			if date_list is None:
				date_list = []
			if re_e_done.match(command) is not None:
				date_list.append(date)
				docno_map[comment] = date_list
				continue
			else:
				date_list = sorted(list(set(date_list)))
				if len(date_list) == 0:
					command += ' (尚未發出)'
				else:
					date_string = ','.join([
						formatted('%03d/%02d/%02d', d) for d in date_list])
					command += ' (' + date_string + ' 已交換)'
		ret_list.append({
			'DATE': date, 'COMMAND': command,
			'COMMENT': comment, 'MAIN_SEQNO': main_num
		})
	return ret_list

def get_topay_single(session, case_stats):
	from func_lib import get_topay_summary
	if ('國稅' in case_stats['SEND_ORG_NAME'] or
		case_stats['EXEC_CASE'] == 2 or
		case_stats['SEND_ORG_ID'] == '107001'):
		return get_topay_summary(
			session, exec_y=case_stats['EXEC_YEAR'],
			exec_t=case_stats['EXEC_CASE'], exec_n1=case_stats['EXEC_SEQNO'])
	else:
		return (
			case_stats['PAY_AMT'] - case_stats['RECEIVE_AMT'] -
			case_stats['RETURN_AMT'] - case_stats['RETURN_AMT_NO'])
