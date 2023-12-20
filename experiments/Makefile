COMMIT ?= $(shell git rev-parse --short HEAD)

.PHONY: all
all:
	papermill ./Analysis.ipynb -p commit ${COMMIT} \
			--no-report-mode Report.ipynb

clean:
	${RM} trivial-*.log solved_pivot_table.tex *.pdf

.PHONY: notebook
notebook:
	jupyter lab --ip 0.0.0.0
