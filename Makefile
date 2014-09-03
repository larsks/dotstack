DOTFILES = $(wildcard *.dot)
SVGFILES = $(DOTFILES:.dot=.svg)
PNGFILES = $(DOTFILES:.dot=.png)

%.svg: %.dot
	dot -Tsvg -o $@ $<
%.png: %.dot
	dot -Tpng -o $@ $<

all: $(SVGFILES) $(PNGFILES)


