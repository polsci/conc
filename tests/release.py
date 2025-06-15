# Test Conc with supported Python versions prior to release
# see nox docs for installing on various platforms
# run with nox -f tests/release.py
# add -v flag for verbose output
# -R flag will use existing envs and not install dependencies again
import nox
import os
import sys

versions = ["3.13", "3.12", "3.11", "3.10"]

def check_avx2_support():
	if os.name == 'nt':
		return False
	return os.system("grep -q avx2 /proc/cpuinfo") == 0

if check_avx2_support():
	print("AVX2 is supported")
else:
	print("AVX2 is not supported")

print("Testing with Python versions:", versions)

@nox.session(python=versions, venv_backend='conda')
def tests(session):
	session.run("python", "--version")
	session.chdir("../")
	session.install("-e", ".[dev]")
	if not check_avx2_support(): # support tests on legacy machine
		if '-R' in sys.argv:
			print("Skipping Polars handling for legacy test with -R flag")
		else:
			session.run("python", "-m", "pip", "uninstall", "-y", "polars")
			session.install("polars-lts-cpu")
	if '-R' in sys.argv:
		print("Skipping spaCy model download with -R flag")
	else:
		session.run("python", "-m", "spacy", "download", "en_core_web_sm")
	session.run("python", "-m", "tests.test_nbs")
	