TODAY := $(shell date "+%B %e, %Y")
METADATA := pandoc-meta.yaml
TEX_TEMPLATE := template.tex
PP := cdsoft-pp
IMAGE_PATH := img
FIGURES := 1.pdf automata.pdf

all: Report.pdf

1.pdf: 1.dot
	dot -Tpdf -o $@ $< -Earrowsize=0.5 -Efontsize=9.0

automata.pdf: automata.dot
	fdp -Tpdf  -Epenwidhth=0.5 -Earrowsize=0.5 -Nwidth=1 -Efontsize=1.0 -o $@ $<


Report.pdf: Report.md ${BIBLIOGRAPHY} ${METADATA} ${TEX_TEMPLATE} ${FIGURES}
	${PP} -img=${IMAGE_PATH}/ $< | pandoc --from markdown \
		--to pdf \
		--standalone \
		--filter pandoc-crossref \
		--filter pandoc-citeproc \
		--highlight-style pygments \
		--metadata date="${TODAY}" \
		-o $@ \
		--metadata-file=${METADATA} \
		--template=${TEX_TEMPLATE}

clean:
	${RM} Report.pdf ${FIGURES}
