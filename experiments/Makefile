COMMIT ?= $(shell git rev-parse --short HEAD)

.PHONY: all
all:
	papermill ./Analysis.ipynb -p commit ${COMMIT} \
			--no-report-mode Report.ipynb
	papermill "SMT-COMP comparison.ipynb" -p commit ${COMMIT} \
			--no-report-mode Report-SMT-COMP.ipynb

clean:
	${RM} trivial-*.log solved_pivot_table.tex *.pdf Report-SMT-COMP.ipynb Report.ipynb

.PHONY: notebook
notebook:
	jupyter lab --ip 0.0.0.0
