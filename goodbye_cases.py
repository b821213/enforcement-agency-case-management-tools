from func_lib import (
	login, get_case_stats, get_case_details, ending_cases, get_topay_summary)
from share_lib import refined_situ_list, print_and_record, get_topay_single
from configs import default_dept
from secret import username_default, password_default
import re
import sys

def get_rejected(situ_list):
	re_rejected = re.compile(r'CY[\d-]{5}退案')
	for index, situ in enumerate(situ_list):
		if re_rejected.search(situ['COMMAND']) is not None:
			return index
	return None

def get_evidence(situ_list):
	re_e_evi = re.compile(r'\d{3}執行憑證')
	re_p_evi = re.compile(r'CY[\d-]{5}債權憑證')
	re_reissue = re.compile(r'CY[\d-]{5}補發債權憑證')
	for index, situ in enumerate(situ_list):
		command = situ['COMMAND']
		if (re_e_evi.search(command) is not None or
			re_p_evi.search(command) is not None or
			re_reissue.search(command) is not None):
			return index
	return None

def get_expired(situ_list):
	re_expired = re.compile(r'CY[\d-]{5}執行期間屆滿通知')
	for index, situ in enumerate(situ_list):
		if re_expired.search(situ['COMMAND']) is not None:
			return index
	return None

def mask_checker(mask, constraint):
	if len(mask) != len(constraint):
		raise IndexError('len(mask) is not equal to len(constraint).')
	else:
		for current, expected in zip(mask, constraint):
			if expected is not None and current != expected:
				return False
	return True

def get_possible_end_situ(session, exec_y, exec_t, exec_n):
	# Returns None if the case has ended.
	# Otherwise, returns a integer list of possible situations.
	stats = get_case_stats(
		session, exec_y=exec_y, exec_t=exec_t, exec_n1=exec_n)[0]
	if stats['END_DATE'] != '':
		return None
	uid = stats['DUTY_IDNO']
	# to reduce the number of queries, undo-amount of cases without interest
	# will be calculated directly.
	case_topay = get_topay_single(session, stats)
	has_cleared = case_topay == 0
	# Two-stage optimization
	# 	Look up topay_summary only if no reasonable ending situations are found
	#	to reduce query cost.
	# In the first stage, less_than_300 is only determined by the current case.
	# If undo amount of current case is greater than 300, it is obviously False.
	# Otherwise, it won't be set correctly until the second stage.
	less_than_300 = False if case_topay > 300 else None
	has_received = stats['RECEIVE_AMT'] > 0
	has_returned = stats['RETURN_AMT'] > 0
	has_uncounted = stats['RETURN_AMT_NO'] > 0
	situ_list = refined_situ_list(
		get_case_details(session, exec_y, exec_t, exec_n)['SITU_LIST'])
	rejected = get_rejected(situ_list)
	evidence = get_evidence(situ_list)
	expired = get_expired(situ_list)
	if rejected is None and evidence is None and expired is None:
		has_rejected, has_evidence, has_expired = False, False, False
	else:
		latest = min(
			[i for i in [rejected, evidence, expired] if i is not None])
		has_rejected = (rejected == latest)
		has_evidence = (evidence == latest)
		has_expired = (expired == latest)
	mask = (
		has_cleared, less_than_300, has_received, has_returned,
		has_uncounted, has_rejected, has_evidence, has_expired)
	# attributes order:
	# has_cleared, less_than_300, has_received, has_returned,
	# has_uncounted, has_rejected, has_evidence, has_expired
	mask_list = [
		((True, None, True, False, False, None, None, None), 1),
		((None, True, True, True, False, None, None, None), 3),
		((True, None, True, True, False, None, None, None), 3),
		((None, None, True, False, False, None, True, None), 4),
		((None, None, False, False, False, None, True, None), 5),
		((None, True, False, True, False, None, None, None), 6),
		((True, None, False, True, False, None, None, None), 6),
		((False, False, False, False, False, True, None, None), 7),
		((None, None, None, None, None, None, None, True), 10),
		((None, None, False, True, False, None, True, None), 12),
		((False, True, True, False, False, None, None, None), 13),
		((None, None, True, True, False, None, True, None), 15),
		((False, True, False, False, False, None, None, None), 22),
		((None, None, False, True, True, None, True, None), 90),
		((None, None, False, False, True, None, True, None), 91),
		((None, True, False, True, True, None, None, None), 92),
		((True, None, False, True, True, None, None, None), 92),
		((False, True, True, False, True, None, None, None), 93),
		((None, None, True, True, True, None, True, None), 94),
		((None, True, True, True, True, None, None, None), 95),
		((True, None, True, True, True, None, None, None), 95),
		((None, None, True, False, True, None, True, None), 96),
		((True, None, False, False, True, None, None, None), 97),
		((True, None, True, False, True, None, None, None), 98)
	]
	results = set(
		[situ for constraint, situ in mask_list
		if mask_checker(mask, constraint) is True])
	if len(results) == 0 and less_than_300 is None:
		less_than_300 = get_topay_summary(session, uid=uid) <= 300
		mask = (
			has_cleared, less_than_300, has_received, has_returned,
			has_uncounted, has_rejected, has_evidence, has_expired)
		results = set(
			[situ for constraint, situ in mask_list
			if mask_checker(mask, constraint) is True])
	return list(results)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print ('使用說明: python [本程式名稱] [輸入檔名 (.csv)] [紀錄檔名 (.csv)]')
		sys.exit(0)
	session = login(username_default, password_default)
	# Reads input into case_list
	print ('讀取輸入檔中...')
	case_list = []
	f_in = open(sys.argv[1], 'r')
	for line in f_in:
		raw = line[:-1].split(',')
		raw += [''] * (5 - len(raw))
		raw[3] = raw[2][:-len(raw[3])] + raw[3]
		y, t, n1, n2, usr_situ = map(lambda s: None if s == '' else int(s), raw)
		if n2 is None:
			n2 = n1
		for n in range(n1, n2 + 1):
			case_list.append([y, t, n, usr_situ])
	f_in.close()
	# Gets possible ending situation(s)
	print ('判斷終結情形...')
	for index, [y, t, n, usr_situ] in enumerate(case_list):
		case_list[index].append(get_possible_end_situ(session, y, t, n))
	# Checks possibility and does ending process
	print ('開始報結...')
	suc_count = 0
	f_err = open(sys.argv[2], 'w', encoding='utf-8-sig')
	for y, t, n, usr_situ, pos_situ in case_list:
		situ = usr_situ
		if pos_situ is None:
			print_and_record ('%03d,%02d,%08d,%s' %
					(y, t, n, '案件已報結/掛結'), file=f_err)
			continue
		if situ is None:
			if len(pos_situ) == 0:
				print_and_record ('%03d,%02d,%08d,%s' %
					(y, t, n, '無適當終結情形'), file=f_err)
				continue
			elif len(pos_situ) > 1:
				print_and_record ('%03d,%02d,%08d,%s' %
					(y, t, n, '多重可能終結情形: %s' %
					str(pos_situ).replace(',', '.')), file=f_err)
				continue
			else:
				situ = pos_situ[0]
		if situ not in pos_situ:
			print_and_record('%03d,%02d,%08d,%s' %
				(y, t, n, '終結情形不合法 (%r)' % pos_situ), file=f_err)
			continue
		status, msg = ending_cases(
			session, default_dept, y, t, n, situ)
		if status is True:
			print ('%03d,%02d,%08d,%s' % (y, t, n, msg))
			suc_count += 1
		else:
			print_and_record ('%03d,%02d,%08d,%s' %
				(y, t, n, msg), file=f_err)
	f_err.close()
	print ('-' * 40)
	print ('成功 %d 件\t失敗 %d 件' % (suc_count, len(case_list) - suc_count))
