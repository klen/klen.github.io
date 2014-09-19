VIRTUALENV=$(shell echo "$${VDIR:-'.env'}")

all: compile

$(VIRTUALENV): requirements.txt
	[ -d $(VIRTUALENV) ] || virtualenv $(VIRTUALENV) --no-site-packages
	$(VIRTUALENV)/bin/pip install -r requirements.txt

clean:
	# mv 404.html 404.bak
	rm -rf *.html author category feeds pages tag theme cache
	# mv 404.bak 404.html
	find . -name "*.py[co]" -delete

compile: $(VIRTUALENV) clean
	$(VIRTUALENV)/bin/pelican $(CURDIR)/_source -o $(CURDIR) -s $(CURDIR)/config.py
	zeta theme

run: $(VIRTUALENV)
	pyserve $(CURDIR)

# compile: clean index.html theme/_main.css
	# @ln -s blog.html category/Blog.html || echo
	# @ln -s books.html category/Books.html || echo
	# @ln -s notes.html category/Notes.html || echo

# books:
	# mogrify -format jpg -background black -gravity center -thumbnail '100x150>' -extent 100x150 $(BOOK_DIR)/*.jpg

# index.html: $(VIRTUALENV)
	# $(PELICAN) $(SOURCE_DIR) -o $(CURDIR) -s $(SETTINGS) -t $(THEME_DIR) -v

# post: compile commit
	# git push

# commit:
	# git add .
	# git add . -u
	# git ci -a

# test: compile
	# open index.html
