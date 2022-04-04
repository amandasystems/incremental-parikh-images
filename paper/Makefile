
%.tex: %.dot
	dot2tex -tmath --encoding utf8 --autosize -ftikz $< > $@

%.pdf: %.tex
	./latexrun $<

.PHONY: FORCE
main.pdf: FORCE main.tex
	./latexrun main.tex

.PHONY: clean
clean:
	./latexrun --clean-all
