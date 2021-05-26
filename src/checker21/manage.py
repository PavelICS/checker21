

from checker21.application import app


def main():
    projects = app.get_projects("libft")
    for project in projects:
        for checker in project.get_checkers():
            print(checker)


if __name__ == "__main__":
    main()
