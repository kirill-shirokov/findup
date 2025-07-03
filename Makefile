.PHONY: all
all: README.md

README.md: doc/readme-header.md generated/usage.txt doc/readme-footer.md
	cat $^ >$@

generated/usage.txt: src/python3/findup.py
	mkdir -p `dirname $@`
	bash -c ". .venv/bin/activate && $< -h >$@"
