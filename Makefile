VIRTUALENV=$(shell echo "$${VDIR:-'.env'}")
PYTHON = $(VIRTUALENV)/bin/python
PELICAN = $(PYTHON) $(CURDIR)/pelican
SOURCE_DIR = $(CURDIR)/_source
SETTINGS = $(SOURCE_DIR)/settings.py
THEME_DIR = $(SOURCE_DIR)/theme
BOOK_DIR = $(THEME_DIR)/static/images/sources/books


all: compile

$(VIRTUALENV): requirements.txt
	virtualenv $(VIRTUALENV) --no-site-packages
	$(VIRTUALENV)/bin/pip install -r requirements.txt

clean: $(VIRTUALENV)
	mv 404.html 404.bak
	rm -rf *.html category feeds tag theme pages author
	mv 404.bak 404.html
	find . -name "*.py[co]" -delete

compile: clean index.html theme/_main.css books
	@ln -s blog.html category/Blog.html || echo
	@ln -s books.html category/Books.html || echo
	@ln -s notes.html category/Notes.html || echo

books:
	mogrify -format jpg -background black -gravity center -thumbnail '100x150>' -extent 100x150 $(BOOK_DIR)/*.jpg

index.html: $(VIRTUALENV)
	$(PELICAN) $(SOURCE_DIR) -o $(CURDIR) -s $(SETTINGS) -t $(THEME_DIR) -v

theme/_main.css: theme
	zeta theme

post: compile commit
	git push

commit:
	git add .
	git add . -u
	git ci -a

test: compile
	open index.html

run:
	pyserve $(CURDIR)
