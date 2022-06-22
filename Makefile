
FIGURES=$(shell grep includegraphics main.tex | grep -v '\\commit' | sed 's/.*{\(.*\)}/\1.pdf/' | tr -s '\n' ' ')

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

.PHONY: copy-figures
copy-figures:
	cp -v ../catra/experiments/{*.pdf,*.tex} graphs/
	sed -I '' 's/Status\.//g' graphs/solved_pivot_table.tex
	sed -I '' 's/MEMORY_OUT/\\textsc{Memory-Out}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/ERROR/\\textsc{Error}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/UNSAT/\\textsc{Unsat}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/TIMEOUT/\\textsc{Timeout}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/SAT/\\textsc{Sat}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/nuxmv/\\Nuxmv/g' graphs/solved_pivot_table.tex
	sed -I '' 's/lazy/\\Calculus/g' graphs/solved_pivot_table.tex
