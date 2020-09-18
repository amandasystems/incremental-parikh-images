LAST_MODIFIED := $(shell date -r Report.md "+%B %e, %Y")
METADATA := pandoc-meta.yaml
TEX_TEMPLATE := template.tex
IMAGE_PATH := img
FIGURES := ${IMAGE_PATH}/1.pdf ${IMAGE_PATH}/automata.pdf

all: Report.pdf

${IMAGE_PATH}/1.pdf: 1.dot
	dot -Tpdf -o $@ $< -Earrowsize=0.5 -Efontsize=9.0

${IMAGE_PATH}/automata.pdf: automata.dot
	fdp -Tpdf  -Epenwidhth=0.5 -Earrowsize=0.5 -Nwidth=1 -Efontsize=1.0 -o $@ $<


Report.pdf: Report.md ${BIBLIOGRAPHY} ${METADATA} ${TEX_TEMPLATE} ${FIGURES}
	pandoc $< --from markdown \
		--to pdf \
		--standalone \
		--filter pandoc-crossref \
		--filter pandoc-citeproc \
		--highlight-style pygments \
		--metadata date="${LAST_MODIFIED}" \
		-o $@ \
		--metadata-file=${METADATA} \
		--template=${TEX_TEMPLATE}

clean:
	${RM} Report.pdf ${FIGURES}
