class SimpleInterpreter:
    def __init__(self):
        # Словарь для хранения переменных: {'name': {'value': val, 'type': type}}
        self.variables = {}
        
        # Словарь для хранения функций
        self.functions = {}
        
        # Словарь для хранения классов
        self.classes = {}
        
        # Стек вызовов для функций (локальные переменные)
        self.call_stack = []
        
        # Поддерживаемые типы данных
        self.valid_types = ['int', 'float', 'string', 'bool', 'void']
        
        # Флаг - находимся ли мы внутри класса при парсинге
        self.current_class = None
    
    def convert_to_type(self, value_str, target_type):
        """
        Преобразует строковое значение в нужный тип
        """
        try:
            if target_type == 'int':
                return int(value_str)
            elif target_type == 'float':
                return float(value_str)
            elif target_type == 'string':
                # Убираем кавычки если есть
                if value_str.startswith('"') and value_str.endswith('"'):
                    return value_str[1:-1]
                return str(value_str)
            elif target_type == 'bool':
                if value_str.lower() in ['true', '1']:
                    return True
                elif value_str.lower() in ['false', '0']:
                    return False
                else:
                    print(f"Ошибка: '{value_str}' не является корректным bool значением")
                    return False
            else:
                print(f"Ошибка: неизвестный тип {target_type}")
                return None
        except ValueError:
            print(f"Ошибка: не удалось преобразовать '{value_str}' в тип {target_type}")
            return None
    
    def get_variable_info(self, var_name):
        """
        Получает информацию о переменной (значение и тип)
        Возвращает словарь {'value': val, 'type': type} или None
        """
        # Сначала ищем в локальных переменных
        if self.call_stack and var_name in self.call_stack[-1]:
            return self.call_stack[-1][var_name]
        # Потом в глобальных
        elif var_name in self.variables:
            return self.variables[var_name]
        else:
            return None
    
    def find_matching_brace(self, lines, start_index):
        """
        Находит закрывающую фигурную скобку для открывающей на start_index
        Возвращает индекс строки с закрывающей скобкой
        """
        brace_count = 0
        for i in range(start_index, len(lines)):
            line = lines[i].strip()
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count == 0:
                    return i
        return -1  # Не найдена
    
    def parse_function_declaration(self, line):
        """
        Парсит объявление функции или метода
        Формат: function name(param1: type1, param2: type2) -> return_type {
        Пример: function add(x: int, y: int) -> int {
        """
        # Убираем { в конце если есть
        line = line.replace('{', '').strip()
        
        parts = line.split()
        if len(parts) < 2:
            return None
            
        keyword = parts[0]  # function или method
        func_declaration = ' '.join(parts[1:])
        
        # Разделяем на имя с параметрами и тип возврата
        if '->' in func_declaration:
            func_part, return_type = func_declaration.split('->', 1)
            return_type = return_type.strip()
        else:
            print("Ошибка: не указан тип возвращаемого значения (используйте ->)")
            return None
        
        # Парсим имя функции и параметры
        paren_pos = func_part.find('(')
        if paren_pos == -1:
            print("Ошибка: неправильный формат объявления функции")
            return None
            
        func_name = func_part[:paren_pos].strip()
        params_str = func_part[paren_pos+1:func_part.rfind(')')].strip()
        
        # Парсим параметры
        params = {}
        if params_str:
            param_list = [p.strip() for p in params_str.split(',')]
            for param in param_list:
                if ':' not in param:
                    print(f"Ошибка: параметр '{param}' должен иметь тип (используйте name: type)")
                    return None
                param_name, param_type = param.split(':', 1)
                param_name = param_name.strip()
                param_type = param_type.strip()
                
                if param_type not in self.valid_types:
                    print(f"Ошибка: неизвестный тип '{param_type}' для параметра '{param_name}'")
                    return None
                    
                params[param_name] = param_type
        
        if return_type not in self.valid_types:
            print(f"Ошибка: неизвестный тип возврата '{return_type}'")
            return None
        
        return {
            'name': func_name,
            'params': params,
            'return_type': return_type,
            'body': [],
            'is_method': keyword == 'method'
        }

    def interpretation(self, code):
        """
        Главная функция - выполняет код нашего языка
        """
        lines = code.strip().split('\n')
        lines = [line.rstrip() for line in lines]  # Убираем пробелы справа

        # Удаляем комментарии и пустые строки
        processed_lines = []
        for line in lines:
            # Убираем комментарии (все что после //)
            comment_pos = line.find('//')
            if comment_pos != -1:
                line = line[:comment_pos].rstrip()

            # Добавляем строку только если она не пустая
            if line.strip():
                processed_lines.append(line)

        lines = processed_lines

        # ФАЗА 1: Парсинг функций и классов
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            words = line.split()
            if not words:
                i += 1
                continue

            # Обработка объявления класса
            if words[0] == 'class':
                if len(words) < 2:
                    print("Ошибка: не указано имя класса")
                    i += 1
                    continue

                class_name = words[1]
                self.current_class = class_name
                self.classes[class_name] = {'methods': {}, 'variables': {}}
                print(f"Найден класс: {class_name}")

                # Найти конец класса по скобкам
                end_index = self.find_matching_brace(lines, i)
                if end_index == -1:
                    print("Ошибка: не найдена закрывающая скобка для класса")
                    break

                # Парсим содержимое класса
                class_content = lines[i + 1:end_index]
                self.parse_class_content(class_content)

                self.current_class = None
                i = end_index + 1
                continue

            # Обработка объявления функции
            elif words[0] == 'function':
                func_info = self.parse_function_declaration(line)
                if func_info is None:
                    i += 1
                    continue

                # Найти тело функции по скобкам
                end_index = self.find_matching_brace(lines, i)
                if end_index == -1:
                    print("Ошибка: не найдена закрывающая скобка для функции")
                    break

                # Читаем тело функции
                func_body = []
                for body_line in lines[i + 1:end_index]:
                    body_line = body_line.strip()
                    if body_line:
                        func_body.append(body_line)

                func_info['body'] = func_body
                self.functions[func_info['name']] = func_info
                print(
                    f"Найдена функция {func_info['name']}({', '.join([f'{name}: {type_}' for name, type_ in func_info['params'].items()])}) -> {func_info['return_type']}")

                i = end_index + 1
                continue



            i += 1

        return lines

    def execute_lines(self, lines):
        # ФАЗА 2: Выполнение основного кода
        in_function_or_class = False
        brace_count = 0

        for line_number, line in enumerate(lines, start=1):
            stripped_line = line.strip()

            if not stripped_line:
                continue

            # Отслеживаем скобки для пропуска кода внутри функций/классов
            if '{' in stripped_line:
                words = stripped_line.split()
                if words and words[0] in ['function', 'method', 'class']:
                    in_function_or_class = True
                    brace_count = 1
                    continue
                elif in_function_or_class:
                    brace_count += stripped_line.count('{')

            if in_function_or_class:
                if '}' in stripped_line:
                    brace_count -= stripped_line.count('}')
                    if brace_count == 0:
                        in_function_or_class = False
                continue

            # Выполняем обычные команды
            try:
                self.execute_line(stripped_line)
            except Exception as e:
                print(f"\n❌ Ошибка на строке {line_number}: {stripped_line}")
                print(f"📌 Сообщение об ошибке: {e}\n")
                break  # или continue — зависит от логики

    
    def parse_class_content(self, class_lines):
        """
        Парсит содержимое класса
        """
        i = 0
        while i < len(class_lines):
            line = class_lines[i].strip()
            if not line:
                i += 1
                continue
                
            words = line.split()
            if not words:
                i += 1
                continue
            
            if words[0] == 'method':
                func_info = self.parse_function_declaration(line)
                if func_info is None:
                    i += 1
                    continue
                
                # Найти конец метода по скобкам
                end_index = self.find_matching_brace(class_lines, i)
                if end_index == -1:
                    print("Ошибка: не найдена закрывающая скобка для метода")
                    break
                
                # Читаем тело метода
                method_body = []
                for body_line in class_lines[i+1:end_index]:
                    body_line = body_line.strip()
                    if body_line:
                        method_body.append(body_line)
                
                func_info['body'] = method_body
                self.classes[self.current_class]['methods'][func_info['name']] = func_info
                print(f"Найден метод {self.current_class}.{func_info['name']}({', '.join([f'{name}: {type_}' for name, type_ in func_info['params'].items()])}) -> {func_info['return_type']}")
                
                i = end_index + 1
            else:
                i += 1

    def evaluate_expression(self, expression_str):
        """
        Вычисляет выражение и возвращает {'value': val, 'type': type}
        """
        expression_str = expression_str.strip()

        # Сначала проверяем, является ли это строковым литералом
        if expression_str.startswith('"') and expression_str.endswith('"'):
            return {'value': expression_str[1:-1], 'type': 'string'}

        # Затем разбиваем по пробелам для других случаев
        parts = expression_str.split()

        if len(parts) == 1:
            # Простое значение
            word = parts[0]

            # Проверяем является ли это литералом
            if word.isdigit() or (word.startswith('-') and word[1:].isdigit()):
                return {'value': int(word), 'type': 'int'}
            elif word.replace('.', '', 1).replace('-', '', 1).isdigit() and word.count('.') == 1:
                return {'value': float(word), 'type': 'float'}
            elif word.lower() in ['true', 'false']:
                return {'value': word.lower() == 'true', 'type': 'bool'}
            else:
                # Это переменная
                var_info = self.get_variable_info(word)
                if var_info is None:
                    raise NameError(f"Переменная '{word}' не найдена")
                return var_info

        elif len(parts) == 3:
            # Арифметическое выражение
            left_info = self.evaluate_expression(parts[0])
            operator = parts[1]
            right_info = self.evaluate_expression(parts[2])

            # Проверяем совместимость типов
            if operator in ['+', '-', '*', '/']:
                if left_info['type'] in ['int', 'float'] and right_info['type'] in ['int', 'float']:
                    left_val = left_info['value']
                    right_val = right_info['value']

                    if operator == '+':
                        result = left_val + right_val
                    elif operator == '-':
                        result = left_val - right_val
                    elif operator == '*':
                        result = left_val * right_val
                    elif operator == '/':
                        if right_val == 0:
                            raise ZeroDivisionError("Деление на ноль")
                        result = left_val / right_val
                        if isinstance(result, float) and result.is_integer():
                            result = int(result)

                    result_type = 'float' if isinstance(result, float) else 'int'
                    return {'value': result, 'type': result_type}
                else:
                    raise TypeError(
                        f"Нельзя применить оператор '{operator}' к типам '{left_info['type']}' и '{right_info['type']}'")

        raise ValueError(f"Не удалось вычислить выражение: '{expression_str}'")
    
    def execute_line(self, line):
        """
        Выполняет одну строку кода
        """
        line = line.rstrip(';').strip()  # Убираем ; в конце
        words = line.split()
        
        if not words:
            return
        
        # Объявление переменной: тип имя = выражение
        if words[0] in self.valid_types and words[0] != 'void':
            if len(words) < 4 or words[2] != '=':
                print(f"Ошибка: неправильный синтаксис объявления переменной")
                return
                
            var_type = words[0]
            var_name = words[1]
            expression = ' '.join(words[3:])
            
            # Вычисляем выражение
            expr_result = self.evaluate_expression(expression)
            
            # Проверяем совместимость типов
            if var_type != expr_result['type']:
                # Пытаемся преобразовать
                converted_value = self.convert_to_type(str(expr_result['value']), var_type)
                if converted_value is None:
                    return
                expr_result = {'value': converted_value, 'type': var_type}
            
            # Сохраняем переменную
            if self.call_stack:
                self.call_stack[-1][var_name] = expr_result
            else:
                self.variables[var_name] = expr_result
                
            print(f"Создана переменная {var_name}: {var_type} = {expr_result['value']}")
        
        elif words[0] == 'print':
            # Вывод переменной
            if len(words) < 2:
                print("Ошибка: не указана переменная для вывода")
                return
                
            var_name = words[1]
            var_info = self.get_variable_info(var_name)
            if var_info is not None:
                print(f"{var_name} ({var_info['type']}): {var_info['value']}")
            else:
                print(f"Ошибка: переменная {var_name} не найдена")
        
        elif words[0] == 'call':
            # Вызов функции
            func_call = ' '.join(words[1:])
            result = self.call_function(func_call)
            if result is not None and result['type'] != 'void':
                print(f"Функция вернула ({result['type']}): {result['value']}")
    
    def call_function(self, func_call_str):
        """
        Вызывает функцию
        """
        paren_pos = func_call_str.find('(')
        if paren_pos == -1:
            print("Ошибка: неправильный формат вызова функции")
            return None
            
        func_name = func_call_str[:paren_pos].strip()
        args_str = func_call_str[paren_pos+1:-1].strip()
        
        if args_str:
            args = [arg.strip() for arg in args_str.split(',')]
        else:
            args = []
        
        if func_name not in self.functions:
            print(f"Ошибка: функция {func_name} не найдена")
            return None
            
        func_info = self.functions[func_name]
        param_names = list(func_info['params'].keys())
        
        if len(args) != len(param_names):
            print(f"Ошибка: функция {func_name} ожидает {len(param_names)} аргументов, получено {len(args)}")
            return None
        
        # Создаем локальный контекст
        local_vars = {}
        
        # Присваиваем значения параметрам с проверкой типов
        for i, param_name in enumerate(param_names):
            param_type = func_info['params'][param_name]
            arg_info = self.evaluate_expression(args[i])
            
            # Проверяем и преобразуем тип если нужно
            if param_type != arg_info['type']:
                converted_value = self.convert_to_type(str(arg_info['value']), param_type)
                if converted_value is None:
                    return None
                arg_info = {'value': converted_value, 'type': param_type}
            
            local_vars[param_name] = arg_info
        
        self.call_stack.append(local_vars)
        
        print(f"Вызов функции {func_name} с параметрами: {[(name, info['value']) for name, info in local_vars.items()]}")
        
        # Выполняем тело функции
        return_value = {'value': None, 'type': func_info['return_type']}
        
        for body_line in func_info['body']:
            # ИСПРАВЛЕНИЕ: Убираем точку с запятой из строки перед обработкой
            body_line = body_line.rstrip(';').strip()
            words = body_line.split()
            if words and words[0] == 'return':
                if len(words) > 1:
                    expression = ' '.join(words[1:])
                    expr_result = self.evaluate_expression(expression)
                    
                    # Проверяем тип возврата
                    if func_info['return_type'] != 'void':
                        if expr_result['type'] != func_info['return_type']:
                            converted_value = self.convert_to_type(str(expr_result['value']), func_info['return_type'])
                            if converted_value is not None:
                                return_value = {'value': converted_value, 'type': func_info['return_type']}
                            else:
                                print(f"Ошибка: нельзя вернуть {expr_result['type']} из функции типа {func_info['return_type']}")
                        else:
                            return_value = expr_result
                break
            else:
                self.execute_line(body_line)
        
        self.call_stack.pop()
        return return_value