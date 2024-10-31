import os
import sys

parsers = ['--recursive-descent', '--lalr']

lib_dir = './lib'
pass_dir = './test/should-pass'
error_dir = './test/should-error'

def test_deduce(deduce_call, path, expected_return = 0, extra_arguments=""):
    deduce_call += ' ' + path
    for parser in parsers:
        call = deduce_call + ' ' + parser + ' ' + extra_arguments
        print('Testing:', call)
        return_code = os.system(call) // 256 # Why does it multiply the return code by 256???
        if return_code != expected_return:
            print(call, 'expected return code', expected_return, 'but got', return_code)
            exit(1)

def generate_deduce_errors(deduce_call, path):
    # We don't pass in the --error flag so we can generate error messages
    # However, that means we can't levarage deduces already existed directory stuff
    # So we manually do it here

    if os.path.isfile(path):
        # TODO: Make sure both paresers produce the same error
        test_deduce(deduce_call, path, 1, '> ' + path + '.err') # this will test both parsers, which should both error
    elif os.path.isdir(path):
        if path[-1] != '/' or path[-1] != '\\': # Windows moment
            path += '/'
        for file in os.listdir(path): 
            if os.path.isfile(path + file):
                if file[-3:] == '.pf':
                    generate_deduce_errors(deduce_call, path + file)
            elif os.path.isdir(path + file):
                # TODO: recursive directories
                pass
    else:
        print(path, 'was not found!')
        exit(1)

def test_deduce_errors(deduce_call, path):
    if os.path.isfile(path):
        if not os.path.isfile(path + '.err'):
            print("Couldn't find an expected error for", path)
            print("Did you mean to generate it? If so, use generate_deduce_errors")
            exit(1)

        temp_file  = './actual_error.tmp' # THIS NEEDS TO BE HARDCODED AND CONSTANT
        test_deduce(deduce_call, path + ' > ' + temp_file, 1)
        ret_code = os.system('diff ' + path + '.err ' + temp_file)
        os.remove(temp_file) # PLEASE MAKE SURE THIS IS HARDCODED AND CONSTANT!!!!!!

        if ret_code != 0:
            print("The error message for", path, "has changed!!!!")
            exit(1)
    else:
        if path[-1] != '/' or path[-1] != '\\': # Windows moment
            path += '/'
        for file in os.listdir(path):
            if os.path.isfile(path + file):
                if file[-3:] == '.pf':
                    test_deduce_errors(deduce_call, path + file)
            elif os.path.isdir(path + file):
                # TODO: recursive directories?
                pass

if __name__ == "__main__":
    # Check command line arguments
    extra_arguments = []

    regenerables = []
    generate_errors = False

    test_lib = False
    test_passable = False
    test_errors = False

    already_processed_next = False
    for i in range(1, len(sys.argv)):
        if already_processed_next:
            already_processed_next = False
            continue
    
        argument = sys.argv[i]
        if argument == '--regenerate-errors':
            generate_errors = True
        elif argument == '--generate-error':
            regenerables.append(sys.argv[i + 1])
            already_processed_next = True
        elif argument == '--lib':
            test_lib = True
        elif argument == '--passable':
            test_passable = True
        elif argument == '--errors':
            test_errors = True
        else:
            print('Unrecognized argument:', argument)
            exit(1)
    
    
    python_path = ""
    for i in range(11, 13):
        python_path = os.popen("command -v python3." + str(i)).read()[0: -1] # strip the newline character with the splicing
        if python_path != "":
            break
    
    if python_path == "":
        print("Could not find a python version at or above 3.11")
        exit(1)
    
    deduce_call = python_path + " ./deduce.py " + " --dir " + lib_dir + " ".join(extra_arguments)

    # Yes there is a chance to optimize this by doing testing the lib directory one time, then adding it to uniquifed modules
    # HOWEVER, I want to make sure the testing suite runs deduce as it normally would
    # So we don't "fix" something in the suite then have it run into errors in actual usage and be like aww shucks

    if generate_errors:
        print('Regenerating ALL errors')
        generate_deduce_errors(deduce_call, error_dir)
    else:
        for generable in regenerables:
            print('Generating error for:', generable)
            generate_deduce_errors(deduce_call, generable)
            generate_errors = True # So we don't run ALL tests

    if test_lib:
        test_deduce(deduce_call, lib_dir)
    if test_passable:
        test_deduce(deduce_call, pass_dir)
    if test_errors:
        test_deduce_errors(deduce_call, error_dir)

    if not (test_lib or test_passable or test_errors or generate_errors):
        test_deduce(deduce_call, lib_dir)
        test_deduce(deduce_call, pass_dir)
        test_deduce_errors(deduce_call, error_dir)
