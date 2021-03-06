# checker21 v0.2.6a

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

Для тестирования libft используется libft-unit-test, split, libft-tester

https://github.com/alelievr/libft-unit-test

https://github.com/Ysoroko/FT_SPLIT_TESTER

https://github.com/Tripouille/libftTester

GetNextLine чекер:
----------------------------

Для тестирования gnl используется gnltester и gnl-war-machine

https://github.com/Tripouille/gnlTester

https://github.com/PavelICS/gnl-war-machine-v2019

Printf чекер:
----------------------------
Для тестирования printf используется pft

https://github.com/gavinfielder/pft

Работа с norminette:
----------------------------
В версии 0.2 появилась расширенная возможность по работе с нормой.

Для работы этого функционала требуется установка оригинального norminette.

checker21 в отличие от классического norminette добавляет:
- подствеку результатов
- кеширование проверок (перепроверяются только последние изменённые файлы)
- проверка только файлов, добавленных в репозиторий (при его наличие)
- отображение только строк с ошибками
- минимальная статистика по норме
- автоматическое исправление ряда базовых, но частых ошибок

Запуск проверки нормы проекта в текущей директории


    $ checker21 norminette
    
Проверка нормы в директории /home/delyn/projects/minishell

    $ checker21 norminette -p /home/delyn/projects/minishell
    

Если что всегда доступен --help, хоть он пока и не очень подробный

Для очистки кеша, на всякий случай перед финальной проверкой, чтоб убедиться, что у вас всё идеально.
Добавьте просто `clear`, где угодно.

    $ checker21 norminette clear
    $ checker21 norminette clear -p /home/delyn/projects/minishell
    $ checker21 norminette -p /home/delyn/projects/minishell clear

Для отображения только ошибок (сокрытие файлов с надписью OK) нужно добавить `errors`.

Например,

    $ checker21 norminette -p /home/delyn/projects/minishell errors

Для просмотра статистики добавляем `stats`

    $ checker21 norminette -p /home/delyn/projects/minishell stats

Автоматическое исправление ошибок от norminette:
----------------------------------------------------

- ⚠ Предварительно нужно проверить проект на норму, исправление ошибок работает с кешем.
- ⚠ Убедитесь, что вы закоммитили все файлы и можете, если что их восстановить. Данный режим находится в стадии тестирования, и в нём могут быть баги, которые могут подпортить ваш код.
- ⚠ Команду нужно запускать несколько раз, т.к. норма сложная штука, за один проход всё не исправить.
- ⚠ После автоматических изменений соберите и проверьте, что ваш проект запускается.
Я проверяю корректность работы программы через создание и просмотр изменений в коммите.
Там сразу видно напортачила программа или нет. Сообщение о баге пишите мне (delyn), приложив файл с ошибкой.
А сам файл придётся подправить ручками по старинке. 

Для запуска автоматического исправления ошибок надо добавить `fix`.
Чтоб checker21 автоматически мог вставлять хедеры в ваши файлы
используйте --user=delyn (не забудьте своего пользака подставить ;)

Например,

    $ checker21 norminette -p /home/delyn/projects/minishell --user=delyn fix
