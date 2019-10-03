from sly import Lexer
from sly import Parser


class VLexer(Lexer):
    tokens = {
        BREAK, CONST, CONTINUE, DEFER, ELSE, ENUM, FN,
        FOR, GO, GOTO, IF, IMPORT, IN, INTERFACE, MATCH,
        MODULE, MUT, OR, PUB, RETURN, STRUCT, TYPE, MAP,
        ASSERT,

        LEFT_SHIFT, RIGHT_SHIFT, EQUALS, NOT_EQUALS,
        LESS_EQUALS, GREATER_EQUALS, LOGICAL_AND,
        LOGICAL_OR,

        ASSIGN_ADD, ASSIGN_SUB, ASSIGN_MUL, ASSIGN_DIV,
        ASSIGN_MOD, ASSIGN_AND, ASSIGN_OR, ASSIGN_XOR,
        ASSIGN_LEFT_SHIFT, ASSIGN_RIGHT_SHIFT, ASSIGN_DECLARE,

        NUMBER, NAME, STRING, CHAR, NEWLINE
    }
    ignore = ' \t'

    literals = {'*', '/', '%', '&', '+', '-', '|', '^', '{', '}', '(', ')', '[', ']', ',', '.', '>', '<', ';'}

    # Keywords (should not have another letter afterwards)
    BREAK = r'break[^a-zA-Z0-9_]'
    CONST = r'const[^a-zA-Z0-9_]'
    CONTINUE = r'continue[^a-zA-Z0-9_]'
    DEFER = r'defer[^a-zA-Z0-9_]'
    ELSE = r'else[^a-zA-Z0-9_]'
    ENUM = r'enum[^a-zA-Z0-9_]'
    FN = r'fn[^a-zA-Z0-9_]'
    FOR = r'for[^a-zA-Z0-9_]'
    GO = r'go[^a-zA-Z0-9_]'
    GOTO = r'goto[^a-zA-Z0-9_]'
    IF = r'if[^a-zA-Z0-9_]'
    IMPORT = r'import[^a-zA-Z0-9_]'
    IN = r'in[^a-zA-Z0-9_]'
    INTERFACE = r'interface[^a-zA-Z0-9_]'
    MATCH = r'match[^a-zA-Z0-9_]'
    MODULE = r'module[^a-zA-Z0-9_]'
    MUT = r'mut[^a-zA-Z0-9_]'
    OR = r'or[^a-zA-Z0-9_]'
    PUB = r'pub[^a-zA-Z0-9_]'
    RETURN = r'return[^a-zA-Z0-9_]'
    STRUCT = r'struct[^a-zA-Z0-9_]'
    TYPE = r'type[^a-zA-Z0-9_]'
    MAP = r'map[^a-zA-Z0-9_]'
    ASSERT = r'assert[^a-zA-Z0-9_]'

    LEFT_SHIFT = r'<<'
    RIGHT_SHIFT = r'>>'
    EQUALS = r'=='
    NOT_EQUALS = 'r!='
    LESS_EQUALS = r'<='
    GREATER_EQUALS = r'>='
    LOGICAL_AND = r'&&'
    LOGICAL_OR = r'\|\|'

    ASSIGN_ADD = r'\+='
    ASSIGN_SUB = r'-='
    ASSIGN_MUL = r'\*='
    ASSIGN_DIV = r'\/='
    ASSIGN_MOD = r'%='
    ASSIGN_AND = r'&='
    ASSIGN_OR = r'\|='
    ASSIGN_XOR = r'\^='
    ASSIGN_LEFT_SHIFT = r'<<='
    ASSIGN_RIGHT_SHIFT = r'>>='
    ASSIGN_DECLARE = r':='

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r"""("([^"\\] | \\.) * ")|('([^'\\]|\\.)*')""")
    def STRING(self, t):
        t.value = t.value[1:-1]
        # TODO: Escaped stuff
        # TODO: String interpolation
        return t

    @_(r'`.`')
    def CHAR(self, t):
        return t[1:-1]

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\/\/.*')
    def COMMENT(self, t):
        pass

    @_(r'[\r\n]+')
    def NEWLINE(self, t):
        self.lineno += t.value.count('\n')
        return t


class VParser(Parser):
    tokens = VLexer.tokens

    precedence = (
        # TODO Assignment?
        # Logical OR
        ('left', 'LOGICAL_OR'),
        # Logical AND
        ('left', 'LOGICAL_AND'),
        # Bitwise OR
        ('left', '|'),
        # Bitwise XOR
        ('left', '^'),
        # Bitwise AND
        ('left', '&'),
        # Equality
        ('left', 'EQUALS', 'NOT_EQUALS'),
        # Relational
        ('left', '<', '>', 'LESS_EQUALS', 'GREATER_EQUALS'),
        # Shift
        ('left', 'RIGHT_SHIFT', 'LEFT_SHIFT'),
        # Additive
        ('left', '+', '-'),
        # Multiplicative
        ('left', '*', '/', '%'),
        # TODO: Unary
        # Postfix
        ('left', '(', '[', '.', 'IN'),
    )

    def __init__(self):
        self.env = {}

    ###################################################################################################
    # Module scope
    ###################################################################################################

    @_('module module_item')
    def module(self, p):
        if p.module_item is None:
            return p.module
        return p.module + [p.module_item]

    @_('module_item')
    def module(self, p):
        if p.module_item is None:
            return []
        return [p.module_item]

    @_('NEWLINE')
    def module_item(self, p):
        pass

    #
    # Function definition
    #

    @_('FN NAME "(" fn_args ")" fn_ret stmt_block')
    def module_item(self, p):
        return ('fn_decl', p.NAME, p.fn_args, p.fn_ret, p.stmt_block)

    @_('')
    def fn_args(self, p):
        return []

    # TODO: Support for a, b int

    @_('fn_args "," NAME maybe_mut maybe_opt type_decl')
    def fn_args(self, p):
        return p.fn_args + [(p.NAME, p.maybe_mut, p.maybe_opt, p.type_decl)]

    @_('NAME type_decl')
    def fn_args(self, p):
        return [(p.NAME, p.type_decl)]

    @_('type_decl')
    def fn_ret(self, p):
        return [p.type_decl]

    @_('')
    def fn_ret(self, p):
        return []

    @_('"(" fn_ret_list ")"')
    def fn_ret(self, p):
        return p.fn_ret_list

    @_('fn_ret_list "," type_decl')
    def fn_ret_list(self, p):
        return p.fn_ret_list + [p.type_decl]

    @_('NAME')
    def fn_ret_list(self, p):
        return [p.NAME]

    #
    # Method definition
    #

    #
    # Struct definition
    #

    @_('STRUCT NAME "{" struct_items "}"')
    def module_item(self, p):
        return ('struct_decl', p.NAME, p.struct_items)

    @_('STRUCT NAME "{"  "}"')
    def module_item(self, p):
        return ('struct_decl', p.NAME, [])

    @_('struct_items struct_item')
    def struct_items(self, p):
        if p.struct_item is None:
            return p.struct_items
        return p.struct_items + [p.struct_item]

    @_('struct_item')
    def struct_items(self, p):
        if p.struct_item is None:
            return []
        return [p.struct_item]

    @_('NAME type_decl NEWLINE')
    def struct_item(self, p):
        return (p.NAME, p.type_decl)

    @_('type_decl NEWLINE')
    def struct_item(self, p):
        return ('', p.type_decl)

    @_('NEWLINE')
    def struct_item(self, p):
        return None

    #
    # Enum definition
    #

    @_('ENUM NAME "{" enum_items "}"')
    def module_item(self, p):
        return ('enum_decl', p.NAME, p.enum_items)

    @_('ENUM NAME "{" "}"')
    def module_item(self, p):
        return ('enum_decl', [])

    @_('enum_items enum_item')
    def enum_items(self, p):
        if p.enum_item is None:
            return p.enum_items
        return p.enum_items + [p.enum_item]

    @_('enum_item')
    def enum_items(self, p):
        if p.enum_item is None:
            return []
        return [p.enum_item]

    @_('NAME')
    def enum_item(self, p):
        return p.NAME

    @_('NEWLINE')
    def enum_item(self, p):
        return None

    #
    # Misc
    #

    @_('MODULE NAME')
    def module_item(self, p):
        return ('module', p.NAME)

    @_('IMPORT NAME')
    def module_item(self, p):
        return ('import', p.NAME)

    ###################################################################################################
    # Statement
    ###################################################################################################

    #
    # Statement list
    #

    @_('"{" stmt_list "}"')
    def stmt_block(self, p):
        return p.stmt_list

    @_('"{" "}"')
    def stmt_block(self, p):
        return []

    @_('stmt_list stmt')
    def stmt_list(self, p):
        if p.stmt is None:
            return p.stmt_list
        return p.stmt_list + [p.stmt]

    @_('stmt')
    def stmt_list(self, p):
        if p.stmt is None:
            return []
        return [p.stmt]

    @_('"{"')
    def com_stmt(self, p):
        return []

    @_('com_stmt stmt')
    def com_stmt(self, p):
        if p.stmt is None:
            return p.com_stmt
        return p.com_stmt + [p.stmt]

    @_('com_stmt "}"')
    def stmt(self, p):
        return p.com_stmt

    #
    # Return stmt
    #

    @_('RETURN return_list_item NEWLINE')
    def stmt(self, p):
        return ('return', p.return_list_item)

    @_('')
    def return_list_item(self, p):
        return []

    @_('return_list_item "," expr')
    def return_list_item(self, p):
        return p.return_list_item + [p.expr]

    @_('expr')
    def return_list_item(self, p):
        return [p.expr]

    #
    # var declaration
    #

    @_('MUT NAME ASSIGN_DECLARE expr NEWLINE')
    def stmt(self, p):
        return ('var_decl', True, p.NAME, p.expr)

    @_('NAME ASSIGN_DECLARE expr NEWLINE')
    def stmt(self, p):
        return ('var_decl', False, p.NAME, p.expr)

    #
    # Variable declaration
    #

    @_('expr NEWLINE')
    def stmt(self, p):
        return p.expr

    #
    # If statement
    #

    @_('IF expr stmt_block NEWLINE')
    def stmt(self, p):
        return ('if', p.expr, p.stmt_block, None)

    @_('IF expr stmt_block ELSE stmt_block NEWLINE')
    def stmt(self, p):
        return ('if', p.expr, p.stmt_block0, p.stmt_block1)

    # TODO: else if...

    #
    # For statement
    #

    @_('FOR stmt_block NEWLINE')
    def stmt(self, p):
        return ('for_ever', p.stmt_block)

    @_('FOR NAME IN expr stmt_block NEWLINE')
    def stmt(self, p):
        return ('for_each', None, p.NAME, p.expr, p.stmt_block)

    @_('FOR NAME "," NAME IN expr stmt_block NEWLINE')
    def stmt(self, p):
        return ('for_each', p.NAME0, p.NAME1, p.expr, p.stmt_block)

    #
    # Assign statement
    #

    @_('expr ASSIGN_ADD expr NEWLINE',
       'expr ASSIGN_SUB expr NEWLINE',
       'expr ASSIGN_MUL expr NEWLINE',
       'expr ASSIGN_DIV expr NEWLINE',
       'expr ASSIGN_MOD expr NEWLINE',
       'expr ASSIGN_AND expr NEWLINE',
       'expr ASSIGN_OR expr NEWLINE',
       'expr ASSIGN_XOR expr NEWLINE',
       'expr ASSIGN_LEFT_SHIFT expr NEWLINE',
       'expr ASSIGN_RIGHT_SHIFT expr NEWLINE',
       )
    def stmt(self, p):
        expr_list = {
            '+=': 'add',
            '-=': 'sub',
            '*=': 'mul',
            '/=': 'div',
            '%=': 'mod',
            '&=': 'bitwise_and',
            '|=': 'bitwise_or',
            '^=': 'bitwise_xor',
            '<<=': 'left_shift',
            '>>=': 'right_shift',
        }
        # This makes sure we have no side effects
        return [
            ('temp_decl', 0, p.expr0),
            ('assign',
             ('temp', 0),
             (expr_list[p[1]],
              ('temp', 0),
              p.expr1
              )
             )
        ]

    #
    # Misc
    #

    @_('DEFER expr NEWLINE')
    def stmt(self, p):
        return ('defer', p.expr)

    @_('BREAK NEWLINE')
    def stmt(self, p):
        return ('break')

    @_('CONTINUE NEWLINE')
    def stmt(self, p):
        return ('continue')

    @_('ASSERT expr NEWLINE')
    def stmt(self, p):
        return ('assert', p.expr)

    @_('expr "=" expr NEWLINE')
    def stmt(self, p):
        return ('assign', p.expr0, p.expr1)

    @_('NEWLINE')
    def stmt(self, p):
        return None

    ###################################################################################################
    # Expressions
    ###################################################################################################

    #
    # Expr list
    #

    @_('expr_list "," expr')
    def expr_list(self, p):
        return p.expr_list + [p.expr]

    @_('expr')
    def expr_list(self, p):
        return [p.expr]

    @_('')
    def expr_list(self, p):
        return []

    #
    # Binary expressions
    #

    @_('expr ">" expr',
       'expr "<" expr',
       'expr NOT_EQUALS expr',
       'expr EQUALS expr',
       'expr LESS_EQUALS expr',
       'expr GREATER_EQUALS expr',
       'expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr',
       'expr "%" expr',
       'expr "&" expr',
       'expr "|" expr',
       'expr "^" expr',
       'expr LOGICAL_AND expr',
       'expr LOGICAL_OR expr',
       'expr LEFT_SHIFT expr',
       'expr RIGHT_SHIFT expr')
    def expr(self, p):
        expr_map = {
            '>': 'greater',
            '<': 'less',
            '!=': 'not_equals',
            '==': 'equals',
            '<=': 'less_equals',
            '>=': 'greater_equals',
            '+': 'add',
            '-': 'sub',
            '*': 'mul',
            '/': 'div',
            '%': 'mod',
            '&': 'bitwise_and',
            '|': 'bitwise_or',
            '^': 'bitwise_xor',
            '||': 'logical_or',
            '&&': 'logical_and',
            '<<': 'left_shift',
            '>>': 'right_shift',
        }
        return (expr_map[p[1]], p.expr0, p.expr1)

    #
    # Misc
    #

    @_('expr "[" expr "]"')
    def expr(self, p):
        return ('access_index', p.expr0, p.expr1)

    @_('expr "(" expr_list ")"')
    def expr(self, p):
        return ('fn_call', p.expr, p.expr_list)

    @_('expr "." expr')
    def expr(self, p):
        return ('member_access', p.expr0, p.expr1)

    @_('expr IN expr')
    def expr(self, p):
        return ('in', p.expr0, p.expr1)

    # WTF?
    # @_('expr OR stmt_block')
    # def expr(self, p):
    #     return ('or', p.expr, p.stmt_block)

    #:
    # Literal expressions
    #

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('"[" expr_list "]"')
    def expr(self, p):
        return ('arr', p.expr_list)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)

    @_('CHAR')
    def expr(self, p):
        return ('chr', p.CHAR)

    ###################################################################################################
    # Helpers
    ###################################################################################################

    @_('NAME')
    def type_decl(self, p):
        return ('base_type', p.NAME)

    @_('"[" "]" type_decl')
    def type_decl(self, p):
        return ('array_type', p.type_decl)

    @_('"&" type_decl')
    def type_decl(self, p):
        return ('ref_type', p.type_decl)

    @_('MAP "[" type_decl "]" type_decl')
    def type_decl(self, p):
        return ('map_type', p.type_decl0, p.type_decl1)

    # TODO: Can we have an optional optional?
    @_('')
    def maybe_opt(self, p):
        return False

    @_('"?"')
    def maybe_opt(self, p):
        return True

    @_('')
    def maybe_mut(self, p):
        return False

    @_('MUT')
    def maybe_mut(self, p):
        return True


if __name__ == '__main__':
    lexer = VLexer()
    parser = VParser()
    text = """
struct User {
	age int 
} 

fn main(a int) {
    color := Color.red
    println(color)
}
"""
    lex = lexer.tokenize(text)
    # for t in lex:
    #     print(t)
    tree = parser.parse(lex)
    print(tree)
