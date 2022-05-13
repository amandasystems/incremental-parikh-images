
FIGURES=choice.pdf no-choice.pdf

%.tex: %.dot
	dot2tex -tmath --encoding utf8 --autosize --crop -ftikz $< > $@

%.pdf: %.tex
	./bin/latexrun $<

%.fig: %.dot
	dot2tex -tmath --encoding utf8 --autosize -ftikz --figonly $< -o $@

.PHONY: FORCE 
main.pdf: FORCE main.tex ${FIGURES}
	./bin/latexrun main.tex

.PHONY: clean
clean:
	./bin/latexrun --clean-all
	${RM} ${FIGURES}

