
import os
import subprocess


def test_notebooks():
	root_dir = '/'.join(os.getcwd().split('/')[: os.getcwd().split('/').index('panel_exp')])
	for directory in ['panel_exp/examples/test_notebooks/', 'panel_exp/examples/deep_dives/']:
		f = os.listdir('%s/%s' % (root_dir, directory))
		for file in f:
			if file.endswith('.ipynb'):
				exit = subprocess.call(["pytest", "--nbmake", '%s/%s%s' % (root_dir, directory, file)])
				assert exit == 0, 'FAIL! %s/%s%s' % (root_dir, directory, file)

				


