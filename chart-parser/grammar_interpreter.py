from dataclasses import dataclass
from lark import Lark, Token, logger, exceptions, tree

class GrammarRule:
    lhs: str
    rhs: str

def interpret_grammar_rules(tokens):
    pass

if __name__ == '__main__':
    print("Running grammar interpreter in like debug mode idk man")
    # Tokenize
    with open("./lark-grammar.lark", encoding='utf-8') as lark_file:
        lark_parser = Lark(lark_file.read(),
                     start='program', parser='lalr',
                     debug=True, propagate_positions=True)
        
    # file = "../Deduce.lark"
    file = "example.lark"
    with open(file, encoding='utf-8') as deduce_lark_file:
        deduce_lark_text = deduce_lark_file.read()
    
    tokens = lark_parser.lex(deduce_lark_text)
    for token in tokens:
        print(repr(token))

    # Parse (interpret grammar rules)


    # Interpret deduce file!!!