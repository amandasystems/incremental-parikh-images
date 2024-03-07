
.PHONY: all
all:
	papermill ./Analysis.ipynb --no-report-mode Report.ipynb
	papermill "SMT-COMP comparison.ipynb" --no-report-mode Report-SMT-COMP.ipynb

clean:
	${RM} *.tex *.pdf Report-SMT-COMP.ipynb Report.ipynb

.PHONY: notebook
notebook:
	jupyter lab --ip 0.0.0.0
