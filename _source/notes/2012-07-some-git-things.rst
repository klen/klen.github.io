Полезности для GIT
##################

:category: Notes
:date: 2012-07-19
:lang: ru
:slug: some-git-things
:tags: git


Алиас для более компактного `git status`:

.. code-block:: shell 

    $ git config --global alias.st 'status -sb'
    $ git st


Алиас для редактирования последнего коммита:

.. code-block:: shell 

    $ git config --global alias.amend 'commit --amend -C HEAD'
    $ git amend


Алиас для отмены последнего коммита:

.. code-block:: shell 

    $ git config --global alias.undo 'reset --soft HEAD^'
    $ git undo


Предпочитаемый мной вывод `diff`:

.. code-block:: shell 

    $ git config --global alias.diff 'diff --word-diff'
    $ git undo


«Визуальная» история веток в консоли:

.. code-block:: shell 

    $ git config --global alias.hist "log --pretty=format:'%Cred%h%Creset %ad | %Cgreen%s%d%Creset [%an]' --graph --date=short"


Удобная работа с `Git-Flow <https://github.com/nvie/gitflow/>`_:

.. code-block:: shell 

    $ git config --global alias.hotfix 'flow hotfix'
    $ git config --global alias.feature 'flow feature'
    $ git config --global alias.release 'flow release'


Автоматическая коррекция опечаток во вводимых командах:

.. code-block:: shell 

    $ git config --global help.autocorrect 1
    $ git comit
    $ git bronch


Автоматическая запись разрешенных мердж конфликтов, для будущего использования:

.. code-block:: shell 

    $ git config --global rerere.enabled 1


Получение веток с не влитыми данными:

.. code-block:: shell 

    $ git branch --no-merged


Список коммитов в ветке *branchA* отсуствующих в ветке *branchB*:

.. code-block:: shell 

    $ git log branchA ^branchB


Многие используют баш функцию `__git_ps1` для вывода названия текущей ветки,
но не все знают, что ее можно сделать более информативной.

.. code-block:: shell 

    # In your .bashrc or .profile:

        GIT_PS1_SHOWDIRTYSTATE=1
        GIT_PS1_SHOWSTASHSTATE=1

        $ (develop *$):


.. _Git: http://ru.wikipedia.org/wiki/Git
