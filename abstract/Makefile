DEPS=$(latexmk -deps main.tex) trace-0.pdf trace-0-aut-0.pdf trace-0.pdf trace-3-aut-0.pdf

%.pdf: %.dot
	dot -Tpdf -o $@ $<

main.pdf: main.tex ${DEPS}
	latexmk -pdf -xelatex $< 

.PHONY: clean
clean:
	latexmk -c
	rm -f trace-0.pdf trace-0-aut-0.pdf trace-0.pdf trace-3-aut-0.pdf

