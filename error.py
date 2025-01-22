from enum import Enum

class VerboseLevel(Enum):
  NONE = 0
  CURR_ONLY = 1
  FULL = 2

# flag for displaying uniquified names

unique_names = False

def set_unique_names(b):
  global unique_names
  unique_names = b

def get_unique_names():
  global unique_names
  return unique_names

# flag for verbose trace

verbose = False

def set_verbose(b):
  global verbose
  verbose = b

def get_verbose():
  global verbose
  if verbose == VerboseLevel.NONE:
    return False
  return verbose

# flag for expect fail

expect_fail_flag = False

def expect_fail():
  return expect_fail_flag

def set_expect_fail(b):
  global expect_fail_flag
  expect_fail_flag = b

# flag for expect static_fail

expect_static_fail_flag = False

def expect_static_fail():
  return expect_static_fail_flag

def set_expect_static_fail(b):
  global expect_static_fail_flag
  expect_static_fail_flag = b
  
def error_header(location):
  # seeing a strange error where some Meta objects don't have a line member.
  if hasattr(location, 'line'):
    return '{file}:{line1}.{column1}-{line2}.{column2}: ' \
        .format(file=location.filename,
                line1=location.line, column1=location.column,
                line2=location.end_line, column2=location.end_column)
            
def warning(location, msg):
  if not expect_fail():
    header = '{file}:{line1}.{column1}-{line2}.{column2}: ' \
        .format(file=location.filename,
                line1=location.line, column1=location.column,
                line2=location.end_line, column2=location.end_column)
    print(header + 'warning: ' + msg)

def error(location, msg):
  raise Exception(error_header(location) + msg)

class IncompleteProof(Exception):
  pass

def incomplete_error(location, msg):
  raise IncompleteProof(error_header(location) + msg)

def last_error(location, msg):
  e = Exception(error_header(location) + msg)
  e.last = True
  raise e

def missing_error(location, msg):
  e = Exception(error_header(location) + msg)
  e.missing = True
  raise e

def warning(location, msg):
  print(error_header(location) + msg)

class StaticError(Exception):
  pass

def static_error(location, msg):
  raise StaticError(error_header(location) + msg)

