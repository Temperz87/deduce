from error import set_verbose, get_verbose
from proof_checker import check_deduce, uniquify_deduce
from abstract_syntax import add_import_directory, print_theorems
import sys
import os
from parser import parse, set_filename, get_filename, set_deduce_directory, init_parser
from lark import exceptions
import traceback

def token_str(token):
    if len(token.value) > 0:
        str = token.value
    else:
        str = token.type
    str = str.lower()
    if str[0] == '$':
        str = str[1:]
    return str

def deduce_file(filename, error_expected):
    try:
        file = open(filename, 'r', encoding="utf-8")
    except OSError:
        print("Couldn't find file:", filename, "to deduce")
        return -1 # File not found
    p = file.read()
    file.close()

    set_filename(filename)
    try:
        if get_verbose():
            print("Deducing file:", filename)
            print("about to parse")
        ast = parse(p, trace=False)
        if get_verbose():
            print("starting uniquify:\n" + '\n'.join([str(d) for d in ast]))
        uniquify_deduce(ast)
        if get_verbose():
            print("finished uniquify:\n" + '\n'.join([str(d) for d in ast]))
        check_deduce(ast)
        if error_expected:
            print('an error was expected in', filename, "but it was not caught")
            return 1 # Failed
        else:
            print_theorems(filename, ast)
            print(filename + ' is valid')

    except exceptions.UnexpectedToken as t:
        if error_expected:
            return 0 # Passed
        else:
            print(get_filename() + ":" + str(t.token.line) + "." + str(t.token.column) \
                  + "-" + str(t.token.end_line) + "." + str(t.token.end_column) + ": " \
                  + "error in parsing, unexpected token: " + token_str(t.token))
            #print('expected one of ' + ', '.join([str(e) for e in t.expected]))
            return 1 # Failed
        
    except Exception as e:
        if error_expected:
            return 0 # Passed
        else:
            print(str(e))
            # Use the following when debugging internal exceptions -Jeremy
            # print(traceback.format_exc())
            # for production, exit
            return 1 # Failed
            # during development, reraise
            # raise e


if __name__ == "__main__":
    # Check command line arguments
    filenames = []
    error_expected = False

    already_processed_next = False
    for i in range(1, len(sys.argv)):
        if already_processed_next:
            already_processed_next = False
            continue
    
        argument = sys.argv[i]

        if argument == '--error':
            error_expected = True
        elif argument == '--verbose':
            set_verbose(True)
        elif argument == '--dir':
            add_import_directory(sys.argv[i+1])
            already_processed_next = True
        elif argument not in filenames:
            filenames.append(argument)
        else:
            print("Got file", argument, "twice, only processing it once")
    
    if len(filenames) == 0:
        print("Couldn't find a file to deduce!")
        exit(1)

    # Start deducing
    sys.setrecursionlimit(5000) # We can probably use a loop for some tail recursive functions

    set_deduce_directory(os.path.dirname(sys.argv[0]))
    init_parser()

    passed = []
    failed = []

    for filename in filenames:
        retcode = deduce_file(filename, error_expected)
        if retcode == 0:
            passed.append(filename)
        elif retcode == 1:
            failed.append(filename)

    if len(failed) == 0:
        if len(passed) >= 1 and len(passed) > 0:
            print("All files are valid")
    else:
        if len(passed) > 1:
            print("Valid: ", ", ".join(passed))
        print("Invalid: ", ", ".join(failed))
