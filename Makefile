
TEXFILES=$(shell grep 'input{'  main.tex | sed -e 's/.*{\([^\}]*.tex\)}/\1/' | tr -s '\n' ' ')
FIGURES=$(shell grep includegraphics main.tex ${TEXFILES} | grep -v '\\commit' | sed -e 's/.*{\([^\}]*\)}/\1.pdf/' | tr -s '\n' ' ')

%.tex: %.dot
	dot2tex -tmath --encoding utf8 --autosize --crop -ftikz $< > $@

%.pdf: %.tex
	./bin/latexrun $<

%.fig: %.dot
	dot2tex -tmath --encoding utf8 --autosize -ftikz --figonly $< -o $@

oopsla24-catra.zip: main.tex Makefile ${TEXFILES} ${FIGURES} mymacros.sty main.bbl bibliography.bib acmart.cls acm-jdslogo.png ACM-Reference-Format.bst
	zip $@ -r graphs $^

main.bbl:
	bibtex main

.PHONY: FORCE 
main.pdf: FORCE main.tex ${FIGURES} ${TEXFILES}
	./bin/latexrun main.tex

.PHONY: clean
clean:
	./bin/latexrun --clean-all
	${RM} ${FIGURES}

# This looks insane, I know, but it was easier to do it this way rather than figuring out how the HELL one renames something something categorical multiindices in Pandas.
.PHONY: copy-figures
copy-figures:
	cp -v experiments/{*.pdf,*.tex} graphs/
	sed -I '' 's/Status\.//g' graphs/solved_pivot_table.tex
	sed -I '' 's/MEMORY_OUT/\\textsc{Memory-Out}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/ERROR/\\textsc{Error}/g' graphs/solved_pivot_table.tex 
	sed -I '' 's/UNSAT/\\textsc{Unsat}/g' graphs/solved_pivot_table.tex graphs/qf_slia_comparison.tex
	sed -I '' 's/TIMEOUT/\\textsc{Timeout}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/SAT/\\textsc{Sat}/g' graphs/solved_pivot_table.tex graphs/qf_slia_comparison.tex
	sed -I '' 's/nuxmv/\\Nuxmv/g' graphs/solved_pivot_table.tex
	sed -I '' 's/PC\*/\\Calculus{}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/nuXmv/\\Nuxmv{}/g' graphs/solved_pivot_table.tex
	sed -I '' 's/Ostrich/\\Ostrich{}/g' graphs/qf_slia_comparison.tex


