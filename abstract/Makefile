DEPS=$(latexmk -deps main.tex)

main.pdf: main.tex ${DEPS}
	latexmk -pdf -xelatex $< 

.PHONY: clean
clean:
	latexmk -c
