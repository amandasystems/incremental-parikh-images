LAST_MODIFIED := $(shell date -r Report.md "+%B %e, %Y")
METADATA := pandoc-meta.yaml
IMAGE_PATH := img
FIGURES := ${IMAGE_PATH}/1.pdf ${IMAGE_PATH}/automata.pdf
PANDOC_OPTIONS := --standalone \
		--filter pandoc-crossref \
		--citeproc \
		--highlight-style pygments \
		--metadata date="${LAST_MODIFIED}" \
		--metadata-file=${METADATA}

all: Report.pdf

${IMAGE_PATH}/nice.pdf: nice-example.dot
	dot -Tpdf -o $@ $< -Earrowsize=0.5


${IMAGE_PATH}/1.pdf: 1.dot
	dot -Tpdf -o $@ $< -Earrowsize=0.5 -Efontsize=9.0

${IMAGE_PATH}/automata.pdf: automata.dot
	fdp -Tpdf  -Epenwidhth=0.5 -Earrowsize=0.5 -Nwidth=1 -Efontsize=1.0 -o $@ $<


Report.pdf: Report.md ${BIBLIOGRAPHY} ${METADATA} ${FIGURES} mymacros.sty
	pandoc ${PANDOC_OPTIONS} $< -o $@

Report.tex: Report.md ${BIBLIOGRAPHY} ${METADATA} ${FIGURES} mymacros.sty
	pandoc ${PANDOC_OPTIONS} $< -o $@

clean:
	${RM} Report.pdf ${FIGURES}
