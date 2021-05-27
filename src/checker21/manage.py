

from checker21.application import app


def main():
    subjects = app.get_subjects("libft")
    for subject in subjects:
        for checker in subject.get_checkers():
            print(checker)


if __name__ == "__main__":
    main()
