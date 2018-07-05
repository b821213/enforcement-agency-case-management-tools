from func_lib import login, read_input, formatted
from func_lib import get_case_stats, get_case_details
from configs import n_show_situ_items
from secret import username_default, password_default
import re
import sys

re_mainno = re.compile(r'\(代表號\d{3}-\d{2}-\d{8}\)')
re_callpay = re.compile(r'\d*/\d*/\d*應到')
re_lookinto = re.compile(r'調查\(.*\)')
re_output = re.compile(r'匯出')
re_e_mainno = re.compile(r'發文字號.{3}\d{3}.\d{8}字')
re_e_docno = re.compile(r'\d{10}[A-Z]')
re_e_done = re.compile(r'已電子公文交換')
re_e_response = re.compile(r'已扣押.*及手續費')
re_three_sheet = re.compile(r'案款收領款繳款暨發\(還\)款通知')
re_launch = re.compile(r'發出文件.*')
re_layaway_start = re.compile(r'CY5-011.*分期')
re_layaway_end = re.compile(r'CY5-01\d限期履行')

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

def check_layaway(situ_list):
	for situ in situ_list:
		command = situ['COMMAND']
		if re_layaway_end.search(command) is not None:
			return None
		elif re_layaway_start.search(command) is not None:
			return situ
	return None

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [輸出檔名 (.csv)]')
	session = login(username_default, password_default)
	f_out = open(sys.argv[2], 'w', encoding='utf8')
	print (','.join(['案號', '義務人', '狀態', '狀態日期']), file=f_out)
	print (','.join(['日期', '內文', '備註', '主案號']), file=f_out)
	for y, t, n in read_input(sys.argv[1]):
		stats = get_case_stats(
			session, exec_y=y, exec_t=t, exec_n1=n, noendbox=False)[0]
		situ_list = refined_situ_list(
			get_case_details(session, exec_y=y, exec_t=t, exec_n=n))
		layaway = check_layaway(situ_list)
		date_sep = lambda s: tuple(map(int, [s[:3], s[3: 5], s[5:]]))
		# check whether it is ended
		if stats['FINISH_DATE'] != '':
			status = '已掛結'
			status_date = date_sep(stats['FINISH_DATE'])
		# check whether it is ending
		elif stats['END_DATE'] != '':
			status = '已報結'
			status_date = date_sep(stats['END_DATE'])
		elif layaway is not None:
			status = '分期中'
			status_date = layaway['DATE']
		else:
			status = ''
			status_date = None
		print (','.join([
			formatted('%03d-%02d-%08d', (y, t, n)), stats['DUTY_NAME'],
			status, formatted('%03d/%02d/%02d', status_date)
			]), file=f_out)
		for situ in situ_list[: n_show_situ_items]:
			print (','.join([
				formatted('%03d/%02d/%02d', situ['DATE']),
				situ['COMMAND'], str(situ['COMMENT']), situ['MAIN_SEQNO']
			]), file=f_out)
		print (',' * (n_show_situ_items - 1), file=f_out)
	f_out.close()