VIRTUAL_ENV ?= env

all: compile

$(VIRTUAL_ENV): requirements.txt
	[ -d $(VIRTUAL_ENV) ] || virtualenv $(VIRTUAL_ENV) --no-site-packages
	$(VIRTUAL_ENV)/bin/pip install -r requirements.txt
	@touch $(VIRTUAL_ENV)

clean:
	# mv 404.html 404.bak
	rm -rf *.html author category feeds pages tag theme cache
	# mv 404.bak 404.html
	find . -name "*.py[co]" -delete

compile: $(VIRTUAL_ENV) clean
	$(VIRTUAL_ENV)/bin/pelican $(CURDIR)/_source -o $(CURDIR) -s $(CURDIR)/config.py
	zeta theme -p "build_" 

follow: $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/pelican $(CURDIR)/_source -o $(CURDIR) -s $(CURDIR)/config.py -r

run: compile
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
