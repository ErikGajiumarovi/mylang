from simple_interpreter import SimpleInterpreter
import os

def run(file_name):
    if not file_name.endswith(".code"):
        print("Ошибка: файл должен иметь расширение .code")
        return
    interpreter = SimpleInterpreter()


    with open(file_name, "r") as file:
        test_code = file.read()

    lines = interpreter.interpretation(test_code)
    print("================== RUN TIME ==================")
    interpreter.execute_lines(lines)


def compile(file_name):
    if not file_name.endswith(".code"):
        print("Ошибка: файл должен иметь расширение .code")
        return

    interpreter = SimpleInterpreter()

    with open(file_name, "r") as file:
        test_code = file.read()

    print("========= COMPILE TIME =========")
    compiled_code = interpreter.interpretation(test_code)

    # Имя выходного файла
    output_file = os.path.splitext(file_name)[0] + ".py"

    # Запись всех строк в новый .py файл
    with open(output_file, "w") as file:
        for line in compiled_code:
            file.write(line + "\n")

    print(f"Компиляция завершена: {output_file}")


if __name__ == "__main__":
    try:
        run("test.code")
    except Exception as e:
        print(f"Ошибка выполнения: {e}")

