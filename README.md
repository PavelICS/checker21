# checker21 v0.1.6a

Установка и запуск:
----------------------------

    $ pip3 install checker21 -U
    
Для установки на школьных компьютерах потребуется добавить checker21 в переменную окружения PATH.
    
    $ echo 'PATH="`dirname ~/any`/Library/Python/3.7/bin:${PATH}"; export PATH' > ~/.checker21
  
    
Запуск производится внутри папки с проектом.

    $ checker21 test [project name]
    
На школьных компьютерах команда checker21 может быть не доступна.
Нам нужно активировать PATH, чтобы команда заработала.
   
    $ source ~/.checker21
  

Доступные проекты для тестирования

- libft
- get_next_line (gnl)
- printf

Пример использования чекера запуска

    $ git clone [url] some_folder
    $ cd some_folder
    $ checker21 test gnl

Чекеры:
----------------------------

Возможен запуск конкретного чекера. По умолчанию запускаются все.
Для запуска конкретного чекера нужно указать его имя:

    $ checker21 test [project name] [check name]

Для многих проектов доступны чекеры общего назначения:

- files
- norminette

files проверят репозиторий на наличие запрещённых файлов.

norminette запускает проверку нормы только для файлов из репозитория и
раскрашивает результаты проверки.

Libft чекер:
----------------------------

Для тестирования libft используется libft-unit-test

https://github.com/alelievr/libft-unit-test

GetNextLine чекер:
----------------------------

Для тестирования gnl используется gnltester и gnl-war-machine

https://github.com/Tripouille/gnlTester

https://github.com/PavelICS/gnl-war-machine-v2019

Printf чекер:
----------------------------
Для тестирования printf используется pft

https://github.com/gavinfielder/pft
