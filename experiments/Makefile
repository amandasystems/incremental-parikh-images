COMMIT ?= $(shell git rev-parse --short HEAD)

.PHONY: all
all:
	./.venv/bin/papermill ./Analysis.ipynb -p commit ${COMMIT} \
			--no-report-mode /dev/null

clean:
	${RM} trivial-*.log solved_pivot_table.tex *.pdf

.PHONY: download-results
download-results:
	rsync --progress capheus:~/catra/${COMMIT}.experiments.log .


.PHONY: notebook
notebook:
	./.venv/bin/jupyter lab
