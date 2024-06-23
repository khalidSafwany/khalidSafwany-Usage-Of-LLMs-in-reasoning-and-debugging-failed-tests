import os
import createAnswerFromLLM


def main():
    directory = 'Hint_study_with_test'
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        _, file_extension = os.path.splitext(file_path)
        if os.path.isfile(file_path) and file_extension == ".json":
            createAnswerFromLLM.get_answer(file_path, filename)


if __name__ == "__main__":
    main()
