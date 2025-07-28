from lexical_analysis import LexicalAnalysis
from simple_interpreter import SimpleInterpreter
import os

from transpiler_functions import example_usage


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


def compile_to_py(file_name):
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

def process_to_phase1(file_name):
    if not file_name.endswith(".code"):
        print("Ошибка: файл должен иметь расширение .code")
        return

    analisys = LexicalAnalysis()

    with open(file_name, "r") as file:
        test_code = file.read()

    print("========= PHASE 1 LexicalAnalysis =========")
    compiled_code = analisys.invoke(test_code)

    # Имя выходного файла
    output_file = os.path.splitext(file_name)[0] + ".phase1"

    # Запись всех строк в новый .py файл
    with open(output_file, "w") as file:
        for line in compiled_code:
            file.write(line + "\n")

def process_to_phase2(file_name):
    if not file_name.endswith(".phase1"):
        print("Ошибка: файл должен иметь расширение .phase1")
        return

    interpreter = SimpleInterpreter()

    with open(file_name, "r") as file:
        test_code = file.read()

    print("========= PHASE 2 =========")
    compiled_code = interpreter.interpretation(test_code)

    # Имя выходного файла
    output_file = os.path.splitext(file_name)[0] + ".phase1"

    # Запись всех строк в новый .py файл
    with open(output_file, "w") as file:
        for line in compiled_code:
            file.write(line + "\n")


if __name__ == "__main__":
    example_usage()

