#!/usr/bin/env python

# test_setup.py - быстрая проверка установки

print("🔍 Проверяем установку...")

# Проверяем Python
import sys
print(f"✅ Python {sys.version}")

# Проверяем llvmlite
try:
    import llvmlite.ir as ir
    import llvmlite.binding as llvm
    print("✅ llvmlite импортирован успешно")
    
    # Инициализация
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    print("✅ LLVM инициализирован")
    
    # Простой тест
    module = ir.Module("test")
    func_type = ir.FunctionType(ir.IntType(32), [])
    function = ir.Function(module, func_type, name="test")
    
    block = function.append_basic_block("entry")
    builder = ir.IRBuilder(block)
    builder.ret(ir.Constant(ir.IntType(32), 42))
    
    print("✅ LLVM IR сгенерирован:")
    print(str(module))
    
    print("\n🎉 Всё работает! Можно начинать разработку компилятора.")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Попробуйте: pip install llvmlite")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")

print(f"\nТекущая папка: {sys.path[0]}")
print("Виртуальное окружение активно!" if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else "⚠️ Виртуальное окружение НЕ активно")