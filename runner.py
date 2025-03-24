import os
import sys
import inspect
import threading
import importlib.util
from pathlib import Path

failed_tests = 0

def _import_from_path(file_):
    module_name = file_.stem
    spec = importlib.util.spec_from_file_location(module_name, file_)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _find_modules(name):
    return Path(os.getcwd()).glob( f"**/tests/{name}")


def _get_functions(arg, predicate, pattern):
    return [obj for name, obj in inspect.getmembers(arg, predicate)
            if name.startswith(pattern)]

def _spawn_threads(funcs, config):
    threads = []
    for func in funcs:
        func_thread = threading.Thread(target=_eval_test(func, config))
        func_thread.start()
        threads.append(func_thread)

    for func_thread in threads:
        func_thread.join()

def _eval_test(func, config):
    args = inspect.signature(func).parameters.keys()
    try:
        if args:
            if not config:
                raise ValueError("Missing conftest")
            params = [getattr(config, arg, None) for arg in args]
            func(*params)
        else:
            func()
    except (AssertionError, BaseException) as e:
        print(f"\033[91m{func.__name__} failed: {str(e)}\033[00m")
        # traceback.print_exc()
        global failed_tests
        failed_tests += 1
    else:
        print(f"\033[92m{func.__name__} succeeded\033[00m")

def _print_init_message(type_):
    print("###########################")
    print(f"Running {type_}-based tests")

def _run_test(obj_, predicate, type_, config):
    if methods := _get_functions(obj_, predicate, "test_"):
        _print_init_message(type_)
        _spawn_threads(methods, config)

def _print_total():
    print("###########################")
    if failed_tests:
        print(f"{failed_tests} {"tests have" if failed_tests > 1 else "test has"} failed!")
    else:
        print("All tests passed successfully!")
        
def main():
    test_files = _find_modules("test_*.py")

    config = None
    if conf_file := next(_find_modules("conftest.py"), None):
        config = _import_from_path(conf_file)

    for t_file in test_files:
        test_obj = _import_from_path(t_file)
        if classes := _get_functions(test_obj, inspect.isclass, "Test"):
            for class_ in classes:
                _run_test(class_(), inspect.ismethod, "class", config)
        _run_test(test_obj, inspect.isfunction, "function", config)

    _print_total()


if __name__ == '__main__':
    main()
