all: pdf

pdf:
	latexmk -pdf main.tex

clean:
	latexmk -C
	rm -f *.run.xml *.bcf

watch:
	latexmk -pvc -pdf main.tex
