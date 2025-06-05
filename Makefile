.PHONY: all
all:	README.md

README.md: doc/readme-header.md generated/usage.txt doc/readme-footer.md
	cat $^ >$@

generated/usage.txt:
	mkdir -p `dirname $@`
	src/python3/findup.py -h >$@
