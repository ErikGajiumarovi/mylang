class CodeTranspiler:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.generated_code = []
        self.indent_level = 0

    def add_line(self, code_line):
        """Добавляет строку с правильными отступами"""
        indent = "    " * self.indent_level
        self.generated_code.append(f"{indent}{code_line}")

    def transpile_to_python(self, your_lang_code):
        """
        Главная функция - транспилирует ваш код в Python
        Возвращает строку с Python кодом
        """
        self.generated_code = []

        # Добавляем заголовок
        self.add_line("# Автоматически сгенерированный Python код")
        self.add_line("# Сгенерировано из вашего языка программирования")
        self.add_line("")

        lines = your_lang_code.strip().split('\n')
        lines = self.preprocess_lines(lines)

        # Фаза 1: Транспиляция функций и классов
        transpiled_lines = self.transpile_definitions(lines)

        # Фаза 2: Транспиляция основного кода
        self.add_line("# Основной код")
        self.add_line("def main():")
        self.indent_level += 1

        # Добавляем словарь для отслеживания типов (упрощенный)
        self.add_line("# Словарь типов переменных для отладки")
        self.add_line("var_types = {}")
        self.add_line("")

        self.transpile_main_code(transpiled_lines)

        self.indent_level -= 1
        self.add_line("")
        self.add_line("if __name__ == '__main__':")
        self.add_line("    main()")

        return '\n'.join(self.generated_code)

    def preprocess_lines(self, lines):
        """Предобработка - удаление комментариев и пустых строк"""
        processed_lines = []
        for line in lines:
            # Убираем комментарии
            comment_pos = line.find('//')
            if comment_pos != -1:
                line = line[:comment_pos].rstrip()

            # Добавляем только непустые строки
            if line.strip():
                processed_lines.append(line)

        return processed_lines

    def transpile_definitions(self, lines):
        """Транспилирует определения функций и классов"""
        remaining_lines = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            words = line.split()

            if not words:
                i += 1
                continue

            # Транспиляция функций
            if words[0] == 'function':
                end_index = self.find_matching_brace(lines, i)
                if end_index != -1:
                    self.transpile_function(lines[i:end_index + 1])
                    i = end_index + 1
                    continue

            # Транспиляция классов
            elif words[0] == 'class':
                end_index = self.find_matching_brace(lines, i)
                if end_index != -1:
                    self.transpile_class(lines[i:end_index + 1])
                    i = end_index + 1
                    continue

            # Остальные строки для основного кода
            remaining_lines.append(line)
            i += 1

        return remaining_lines

    def transpile_function(self, func_lines):
        """Транспилирует функцию в Python"""
        header = func_lines[0].strip()

        # Парсим заголовок функции
        func_info = self.parse_function_header(header)
        if not func_info:
            return

        # Генерируем Python функцию
        params_str = ', '.join(func_info['params'].keys())
        self.add_line(f"def {func_info['name']}({params_str}):")
        self.indent_level += 1

        # Добавляем проверки типов параметров
        for param_name, param_type in func_info['params'].items():
            self.add_line(f"# Параметр {param_name}: {param_type}")

        # Транспилируем тело функции
        body_lines = func_lines[1:-1]  # Убираем заголовок и закрывающую скобку
        if body_lines:
            for body_line in body_lines:
                self.transpile_statement(body_line.strip())
        else:
            self.add_line("pass")

        self.indent_level -= 1
        self.add_line("")

    def transpile_class(self, class_lines):
        """Транспилирует класс в Python"""
        header = class_lines[0].strip()
        words = header.split()
        class_name = words[1] if len(words) > 1 else "UnknownClass"

        self.add_line(f"class {class_name}:")
        self.indent_level += 1

        # Транспилируем методы класса
        i = 1
        has_methods = False
        while i < len(class_lines) - 1:
            line = class_lines[i].strip()
            if line.startswith('method'):
                end_index = self.find_matching_brace(class_lines, i)
                if end_index != -1:
                    method_lines = class_lines[i:end_index + 1]
                    self.transpile_method(method_lines)
                    has_methods = True
                    i = end_index + 1
                    continue
            i += 1

        if not has_methods:
            self.add_line("pass")

        self.indent_level -= 1
        self.add_line("")

    def transpile_method(self, method_lines):
        """Транспилирует метод класса в Python"""
        header = method_lines[0].strip()

        # Парсим заголовок метода (похож на функцию, но добавляем self)
        func_info = self.parse_function_header(header.replace('method', 'function'))
        if not func_info:
            return

        # Генерируем Python метод
        params_list = ['self'] + list(func_info['params'].keys())
        params_str = ', '.join(params_list)
        self.add_line(f"def {func_info['name']}({params_str}):")
        self.indent_level += 1

        # Транспилируем тело метода
        body_lines = method_lines[1:-1]
        if body_lines:
            for body_line in body_lines:
                self.transpile_statement(body_line.strip())
        else:
            self.add_line("pass")

        self.indent_level -= 1
        self.add_line("")

    def transpile_main_code(self, lines):
        """Транспилирует основной код программы"""
        if not lines:
            self.add_line("pass")
            return

        for line in lines:
            self.transpile_statement(line.strip())

    def transpile_statement(self, line):
        """Транспилирует одну инструкцию"""
        if not line or line == '}':
            return

        line = line.rstrip(';').strip()
        words = line.split()

        if not words:
            return

        # Объявление переменной: тип имя = выражение
        if words[0] in ['int', 'float', 'string', 'bool']:
            self.transpile_variable_declaration(line)

        # Команда print
        elif words[0] == 'print':
            self.transpile_print(line)

        # Вызов функции
        elif words[0] == 'call':
            self.transpile_function_call(line)

        # Return statement
        elif words[0] == 'return':
            self.transpile_return(line)

        # Присвоение существующей переменной
        elif '=' in line and not any(line.startswith(t) for t in ['int', 'float', 'string', 'bool']):
            self.transpile_assignment(line)

        else:
            self.add_line(f"# Неизвестная инструкция: {line}")

    def transpile_variable_declaration(self, line):
        """Транспилирует объявление переменной"""
        words = line.split()
        if len(words) >= 4 and words[2] == '=':
            var_type = words[0]
            var_name = words[1]
            expression = ' '.join(words[3:])

            # Конвертируем выражение в Python
            py_expression = self.transpile_expression(expression)

            self.add_line(f"# {var_type} {var_name}")
            self.add_line(f"{var_name} = {py_expression}")
            self.add_line(f"var_types['{var_name}'] = '{var_type}'")

    def transpile_assignment(self, line):
        """Транспилирует присвоение значения существующей переменной"""
        parts = line.split('=', 1)
        if len(parts) == 2:
            var_name = parts[0].strip()
            expression = parts[1].strip()
            py_expression = self.transpile_expression(expression)

            self.add_line(f"{var_name} = {py_expression}")

    def transpile_print(self, line):
        """Транспилирует команду print"""
        words = line.split()
        if len(words) >= 2:
            var_name = words[1]
            self.add_line(f"if '{var_name}' in var_types:")
            self.indent_level += 1
            self.add_line(f"print(f'{var_name} ({{var_types[\"{var_name}\"]}}): {{{var_name}}}')")
            self.indent_level -= 1
            self.add_line(f"else:")
            self.indent_level += 1
            self.add_line(f"print('Ошибка: переменная {var_name} не найдена')")
            self.indent_level -= 1

    def transpile_function_call(self, line):
        """Транспилирует вызов функции"""
        func_call = line[5:].strip()  # Убираем 'call '
        paren_pos = func_call.find('(')
        if paren_pos != -1:
            func_name = func_call[:paren_pos]
            args_str = func_call[paren_pos + 1:-1]

            if args_str.strip():
                py_args = [self.transpile_expression(arg.strip()) for arg in args_str.split(',')]
                args_str = ', '.join(py_args)
            else:
                args_str = ''

            self.add_line(f"func_result = {func_name}({args_str})")
            self.add_line(f"if func_result is not None:")
            self.add_line(f"    print(f'Функция вернула: {{func_result}}')")

    def transpile_return(self, line):
        """Транспилирует return statement"""
        words = line.split()
        if len(words) > 1:
            expression = ' '.join(words[1:])
            py_expression = self.transpile_expression(expression)
            self.add_line(f"return {py_expression}")
        else:
            self.add_line("return None")

    def transpile_expression(self, expression):
        """Конвертирует выражение в Python синтаксис"""
        expression = expression.strip()

        # Строковый литерал
        if expression.startswith('"') and expression.endswith('"'):
            return expression

        # Булевы значения
        if expression.lower() == 'true':
            return 'True'
        elif expression.lower() == 'false':
            return 'False'

        # Числа остаются как есть
        if expression.replace('.', '', 1).replace('-', '', 1).isdigit():
            return expression

        # Арифметические выражения
        parts = expression.split()
        if len(parts) == 3:
            left = self.transpile_expression(parts[0])
            operator = parts[1]
            right = self.transpile_expression(parts[2])
            return f"({left} {operator} {right})"

        # Переменная - используем просто имя переменной, а не словарь
        return expression

    def parse_function_header(self, header):
        """Парсит заголовок функции (упрощенная версия из оригинала)"""
        header = header.replace('{', '').strip()
        parts = header.split()

        if len(parts) < 2:
            return None

        func_declaration = ' '.join(parts[1:])

        if '->' not in func_declaration:
            return None

        func_part, return_type = func_declaration.split('->', 1)
        return_type = return_type.strip()

        paren_pos = func_part.find('(')
        if paren_pos == -1:
            return None

        func_name = func_part[:paren_pos].strip()
        params_str = func_part[paren_pos + 1:func_part.rfind(')')].strip()

        params = {}
        if params_str:
            param_list = [p.strip() for p in params_str.split(',')]
            for param in param_list:
                if ':' in param:
                    param_name, param_type = param.split(':', 1)
                    params[param_name.strip()] = param_type.strip()

        return {
            'name': func_name,
            'params': params,
            'return_type': return_type
        }

    def find_matching_brace(self, lines, start_index):
        """Находит соответствующую закрывающую скобку"""
        brace_count = 0
        for i in range(start_index, len(lines)):
            line = lines[i].strip()
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count == 0:
                    return i
        return -1

    def save_to_file(self, python_code, filename="generated_code.py"):
        """Сохраняет сгенерированный Python код в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(python_code)
        print(f"Python код сохранен в файл: {filename}")


# Пример использования:
def example_usage():
    transpiler = CodeTranspiler()

    # Ваш код
    your_code = '''
    function add(x: int, y: int) -> int {
        return x + y;
    }

    int result = 10;
    call add(5, 3);
    print result;
    '''

    # Генерируем Python код
    python_code = transpiler.transpile_to_python(your_code)

    # Сохраняем в файл
    transpiler.save_to_file(python_code)

    return python_code