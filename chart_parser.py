from abstract_syntax import *
from dataclasses import dataclass
from error import *
from lark import Lark, Token, Tree, logger, exceptions
from parser import get_filename, get_deduce_directory, infix_ops, operator_symbol, prefix_ops
from rec_desc_parser import meta_from_tokens
# import logging

#logger.setLevel(logging.DEBUG)

modules = []

@dataclass
class ProductionRule:
    name: str
    meta: Meta
    expected: list # expected list of rules

    def applicable(self, chart : list) -> bool:
        return False # mfw no abstract classes

    def __str__(self):
        return self.name + ': ' + str(self.meta)
    
# For when we're looking for like sequences of characters
# e.g. in "if" bool "then" bool "else" bool "if" and "then" would be literals 
@dataclass
class LiteralRule(ProductionRule):
    literal: str

    def applicable(self, chart : list) -> bool:
        return chart[0] == self.literal 

    def __str__(self):
        return self.literal + ': ' + str(self.meta)

@dataclass
class TypeRule(ProductionRule):
    rules: list[ProductionRule]

    def applicable(self, chart : list) -> bool:
        for rule in self.rules:
            if rule.applicable(chart):
                return True
        return False
    
    def __str__(self):
        return self.name + "[" + [str(x) for x in self.rules]

@dataclass
class Item:
    p: TypeRule # partial parse tree
    i: int # left extent inclusive
    j: int # right extent noninclusive

    # TODO: Add type information into the item somehow
    def __str__(self):
        return str(self.p) + ' [' + str(self.i) + ', ' + str(self.j) + ']'

lark_parser = None

def init_parser():
  global lark_parser
  lark_file = get_deduce_directory() + "/Deduce-chart.lark"
  lark_parser = Lark(open(lark_file, encoding="utf-8").read(),
                     start='program', parser='lalr',
                     debug=True, propagate_positions=True)

##################################################
# Chart Parsing Concrete Syntax to Parse Tree
##################################################

def pretty_print_tokens(token_list):
    for token in token_list:
        if isinstance(token, list):
            print('{ ', end='')
            for token2 in token:
                print(str(token2) + ', ', end='')
            print('}, ', end='')
        else:
            print(str(token) + ', ', end='')
    print('END')

grammar_rules = {}

def add_grammar(id, rules):
    if id not in grammar_rules:
        grammar_rules[id] = []
    for rule in rules:
        grammar_rules[id].append(rule)
            
def collect_union(tokens, i):
    if tokens[i].type != 'UNION':
        print("Tried to collect a union on token", repr(tokens[i]))
        exit(1)
    i += 1
    if tokens[i].type != 'IDENT':
        print("Expected an ident token but got ", repr(tokens[i]), "instead")
    union_name = tokens[i].value
    i += 1

    if tokens[i].value != '{':
        print("Expected the \'{\' token but got ", repr(tokens[i]), "instead")

    union_representations = []

    while tokens[i].value != '}':
        if i > len(tokens):
            print("Union type", union_name, "not closed!!!")
            exit(1)
        union_representations.append(tokens[i])
        i += 1
    
    print('Got union', union_name, 'represented by:', ','.join(union_representations))

    # add_grammar('type', )
    exit(0)

def add_builtin_rules():
    add_grammar('union', )





























































def parse(program_text, trace = False, error_expected = False):
  trace = True
  if trace:
    print('lexing!')
  lexed = lark_parser.lex(program_text)

  tokens = []
  if trace:
    print('tokens:')
    for word in lexed:
        print('\t', repr(word))
        tokens.append(word)
    
  while True: # TODO: Condition
    newitems = []
    for i in range(len(tokens)):
        myTrees = []
        print("On", tokens[i])

        if not tokens[i].type in grammar_rules:
            continue
        rules = grammar_rules[tokens[i].type]
        for rule in rules: 
            # print("Trying to parse", tokens[i], "with rule", rule)
            if rule.can_apply(i, tokens):
                myTrees.append(rule.apply_rule(i, tokens, meta_from_tokens(tokens[i], tokens[i])))
                # print("\tApplied")
            else:
                # print("\tCouldn't apply")
                pass
        if len(myTrees) > 0:
            newitems.append((i, myTrees))
        

    if len(newitems) == 0: 
        break # We are either done or have a parse error
    for i,trees in newitems:
        print("Got newitem(s)")
        pretty_print_tokens(trees)
        pretty_print_tokens(tokens)
        tokens = tokens[0:i] + [trees] + tokens[i + 1:]
        pretty_print_tokens(tokens)
    
    print("Final:")
    for thing in tokens:
        if isinstance(thing, List):
            print('\t' + ' or '.join([str(x) for x in thing]))
        else:
            print('\t' + str(thing))
    exit(0)
        
