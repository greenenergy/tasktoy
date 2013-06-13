PPATH = "../"
.PHONY: test_proj
test_proj:
	rm -f *.log
	@(export PYTHONPATH=$(PPATH) ; ./test_all.py)

clean:
	rm -f *.pyc  *.log profile.out

