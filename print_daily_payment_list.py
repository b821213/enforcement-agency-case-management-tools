from func_lib import login, download_payment_list
from share_lib import read_input
from secret import username_stats_manager, password_stats_manager
from configs import adobe_reader_path, default_payment_list_path, payment_wait_time
import sys
import subprocess
from time import sleep

if __name__ == '__main__':
	if len(sys.argv) != 1:
		print ('使用說明: python [本程式名稱]')
		sys.exit(0)
	y, m, d = map(int, input('請輸入查詢年月日 (yyy/mm/dd): ').split('/'))
	date = (y, m, d)
	session = login(username_stats_manager, password_stats_manager)
	dept_list = [
		'乙', '丁', '仁', '平', '甲', '孝', '和',
		'忠', '信', '愛', '義', '德', '禮'
	] 
	undo = []
	for index, dept in enumerate(dept_list):
		try:
			print ('(%d/%d) %s ' % (index + 1, len(dept_list), dept), end='')
			if download_payment_list(
				session, date_s=date, date_e=date, dept=dept,
				show_hi=False, show_li=False, show_electronic=False) is False:
				raise Exception('下載失敗')
			print ('列印中')
			proc = subprocess.Popen(
				[adobe_reader_path, '/t', default_payment_list_path])
			sleep(payment_wait_time)
			proc.kill()
		except Exception as e:
			print (e)
			undo.append(dept)
	if len(undo) > 0:
		print ('未列印清單:')
		print ('\t%s' % ''.join(undo))
