import os
import sys
import glob
import inspect
import threading
import importlib.util
from inspect import isfunction, ismethod, isclass


failed_tests = 0

def _import_from_path(file_):
    module_name = ".py".split(os.path.basename(file_))[0]  # Path(path).stem ?!
    spec = importlib.util.spec_from_file_location(module_name, file_)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _find_modules(dir_path, name):
    glob_pattern = os.path.join(dir_path, f"tests/{name}")
    return glob.glob(glob_pattern)

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

def _print_total():
    print("###########################")
    if failed_tests:
        print(f"{failed_tests} {"tests have" if failed_tests > 1 else "test has"} failed!")
    else:
        print("All tests passed successfully!")


def main(path_):
    dir_path = f"{os.path.dirname(path_)}*"
    test_files = _find_modules(dir_path, "test_*.py")

    config = None
    if conf_file := _find_modules(dir_path, "conftest.py"):
        config = _import_from_path(conf_file[0])

    for t_file in test_files:
        test_obj = _import_from_path(t_file)
        if funcs := _get_functions(test_obj, isfunction, "test_"):
            _print_init_message("function")
            _spawn_threads(funcs, config)

        if classes := _get_functions(test_obj, isclass, "Test"):
            for class_ in classes:
                methods = _get_functions(class_(), ismethod, "test_")
                _print_init_message("class")
                _spawn_threads(methods, config)

    _print_total()


if __name__ == '__main__':
    main(sys.argv[0])