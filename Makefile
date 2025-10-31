PDF=main.pdf
TEX=main.tex

all:pdf

pdf:
	latexmk -pdf -interaction=nonstopmode - halt-on-error $(TEX)
	
clean:
	latexmk -C
	rm -f $(PDF)
	
.PHONX: all pdf clean