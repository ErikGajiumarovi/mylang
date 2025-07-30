class LexicalAnalysis:
    # Класс для лексического анализа кода на нашем языке
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

    def invoke(self, code):
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
