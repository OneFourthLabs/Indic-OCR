from subprocess import Popen, PIPE, STDOUT

def run_command(command):
	out = Popen(command.split(), shell=True, stdout=PIPE, stderr=STDOUT)
	stdout, stderr = out.communicate()
	if stderr:
		stderr = stderr.decode("utf-8").strip()
		print(stderr)
	return stdout.decode("utf-8").strip().replace('\r\n', '\n')
