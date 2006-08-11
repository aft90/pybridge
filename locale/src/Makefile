#Generic rule for MO files
%.mo: DIR1 = ../$(basename $@)
%.mo: DIR2 = $(DIR1)/LC_MESSAGES
%.mo: %.po
	##############
	#GENERATING $@
	##############
	if [ ! -d $(DIR1) ]; then mkdir $(DIR1); fi
	if [ ! -d $(DIR2) ]; then mkdir $(DIR2); fi
	msgfmt $< -o $@
	cp $@ $(DIR2)/pybridge.mo

#Generic rule for PO files
%.po: pybridge.pot
	##################
	#MERGING $@ AND $<
	##################
	msgmerge -UN $@ $<

#Generic rule for POT files
%.pot: ../../glade/pybridge.glade ../../pybridge/ui/*.py
	############
	#CREATING $@
	############
	intltool-extract --type=gettext/glade ../../glade/pybridge.glade
	xgettext -k_ -kN_ --from-code=UTF-8 -o $@ ../../glade/pybridge.glade.h ../../pybridge/ui/*.py

update: $(shell ls *.po)

all: $(subst .po,.mo,$(shell ls *.po))

clean:
	rm *.mo ../../glade/pybridge.glade.h
