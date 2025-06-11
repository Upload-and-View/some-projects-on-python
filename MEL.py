import re
import math

# --- 1. Lexer (Tokenization) ---

class Token:
    """Represents a lexical token in the MEL language."""
    def __init__(self, type, value, line=None, column=None):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value

# Define token types and their regular expressions.
# Order matters: longer, more specific patterns should come before shorter, general ones.
TOKEN_SPECIFICATIONS = [
    # Program Structure
    ('PROGRAM_START', r':::\s*Program\s*start'), # Changed from :: to :::
    ('PROGRAM_END', r';;;\s*Program\s*end'),

    # Comments (Pure comments first to consume the whole line)
    ('COMMENT_PURE', r'>\s*~.*'),
    ('COMMENT_SINGLE', r'~.*'),

    # Literals
    ('STRING', r'"(?:[^"\\]|\\.)*"'), # Handles escaped quotes and newlines (with re.DOTALL flag)
    ('ARRAY_START', r'\['), # Changed from ` to [
    ('ARRAY_END', r'\]'),   # Changed from ` to ]
    ('REAL_NUMBER', r'#+(?::#+)*'), # e.g., ###:#:####
    ('BINARY_LITERAL_PREFIX', r';;'), # e.g., ;;$$$$$$$$;$$$$$$$

    # Operators (Multi-character operators before single-character ones, and before literals)
    # CRITICAL: Order operators before literals that might share prefixes!
    ('REAL_LE_EQ', r'#<='),
    ('REAL_GE_EQ', r'#>='),
    ('REAL_NE_EQ', r'#!='),
    ('BINARY_LE_EQ', r'\$<='),
    ('BINARY_GE_EQ', r'\$>='),
    ('BINARY_NE_EQ', r'\$!='),
    ('REAL_ADD', r'#\+'),
    ('REAL_SUB', r'#-'),
    ('REAL_MUL', r'#\*'),
    ('REAL_DIV', r'#/'),
    ('REAL_FACTORIAL', r'#!'),
    ('REAL_SQRT', r'#\\'), # Escaped backslash
    ('REAL_MOD', r'#%'),
    ('REAL_POW', r'#\^'),
    ('BINARY_ADD', r'\$\+'),
    ('BINARY_SUB', r'\$-'),
    ('BINARY_MUL', r'\$\*'),
    ('BINARY_DIV', r'\$/'), # Ensure this comes before binary literals like $$$$$$
    ('BINARY_FACTORIAL', r'\$!'),
    ('BINARY_SQRT', r'\$\\'), # Escaped backslash
    ('BINARY_MOD', r'\$%'),
    ('BINARY_POW', r'\$\^'),
    ('REAL_LT', r'#<'),
    ('REAL_EQ', r'#='),
    ('REAL_GT', r'#>'),
    ('BINARY_LT', r'\$<'),
    ('BINARY_EQ', r'\$='), # Ensure this comes before binary literals like $$$
    ('BINARY_GT', r'\$>'),
    ('ASSIGN', r'='),
    ('UNARY_NEGATE', r'\|'),

    # Specific binary literals (after operators that might share prefixes)
    ('BINARY_BIT_ONE', r'\$\$\$\$\$\$\$\$'), # Single binary digit 1
    ('BINARY_BIT_ZERO', r'\$\$\$\$\$\$\$'), # Single binary digit 0
    ('BINARY_ZERO_DECIMAL', r'\$\$\$\$\$\$'), # Decimal 0
    ('BINARY_EMPTY', r'\$\$\$\$\$'), # Empty, non-existent (e.g., empty list/string)
    ('BINARY_ABSENCE', r'\$\$\$\$'), # Absence of value (None)
    ('BINARY_TRUE', r'\$\$\$'), # Boolean true
    ('BINARY_FALSE', r'\$\$'), # Boolean false

    # Input/Output & Function Call Prefix
    ('INPUT', r'<'),
    ('OUTPUT_REVERSED', r'>>'), # Longer operator before shorter prefix
    ('OUTPUT_NORMAL', r'<<'),   # Longer operator before shorter prefix
    ('OUTPUT_CHAR', r'>'),      # Shorter prefix for multi-char output
    ('FUNCTION_CALL_PREFIX', r'->>'), # Also used for array functions

    # Control Flow
    ('TRY', r'%%'),
    ('CATCH', r'%%%%'),
    ('IF', r'\?'),
    ('ELSE_IF', r'\?\?#'),
    ('ELSE', r'\?\?:'),
    ('END_LOOP', r'!@!'), # Longer operator before shorter prefix
    ('END_CONDITIONAL', r'!'), # Shorter prefix for loop end
    ('WHILE_LOOP', r'@'),
    ('FOR_LOOP', r'#@#'),

    # Functions
    ('FUNCTION_DEF', r'->'),
    ('RETURN', r'\^'),

    # Delimiters
    ('COMMA', r','),
    ('SEMICOLON_DELIMITER', r';'), # Used in binary number construction
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('COLON', r':'), # Added for eval-like function call

    # Identifiers (variables, function names)
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),

    # Whitespace (to be ignored)
    ('WHITESPACE', r'\s+'),

    # Catch-all for any remaining character (to be ignored as per user request)
    ('UNKNOWN', r'.'),
]

class Lexer:
    """Converts MEL source code into a stream of Tokens."""
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def _advance_pos(self, length):
        """Helper to update position, line, and column."""
        for _ in range(length):
            if self.pos < len(self.text):
                if self.text[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1

    def get_tokens(self):
        """Tokenizes the input text and returns a list of Tokens."""
        while self.pos < len(self.text):
            match = None
            current_line = self.line
            current_column = self.column

            for token_type, pattern in TOKEN_SPECIFICATIONS:
                # Use re.DOTALL for STRING pattern to allow newlines
                regex_flags = re.DOTALL if token_type == 'STRING' else 0
                regex = re.compile(pattern, regex_flags)
                
                m = regex.match(self.text, self.pos)
                if m:
                    value = m.group(0)
                    if token_type == 'WHITESPACE' or token_type.startswith('COMMENT'):
                        # Ignore whitespace and comments
                        pass
                    elif token_type == 'UNKNOWN':
                        # Ignore unknown characters as requested
                        pass
                    else:
                        token = Token(token_type, value, current_line, current_column)
                        self.tokens.append(token)
                    
                    self._advance_pos(len(value)) # Update position, line, column
                    match = True
                    break
            
            if not match:
                raise Exception(f"Lexer Error: Unprocessable character '{self.text[self.pos]}' at line {self.line}, column {self.column}")
        return self.tokens

# --- 2. Parser (AST Construction) ---

class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""
    def __repr__(self):
        # Generic representation for debugging
        attrs = ', '.join(f"{k}={getattr(self, k)!r}" for k in self.__dict__ if not k.startswith('_'))
        return f"{self.__class__.__name__}({attrs})"

# Specific AST Node Types
class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class AssignmentNode(ASTNode):
    def __init__(self, var_name_token, value_expr):
        self.var_name = var_name_token.value
        self.value_expr = value_expr

class StringLiteralNode(ASTNode):
    def __init__(self, token):
        self.value = token.value[1:-1] # Remove quotes

class BinaryLiteralNode(ASTNode):
    def __init__(self, token_value):
        # token_value can be '$$', '$$$', ';;$$$$$$$;$$$$$$$$', etc.
        self.raw_value = token_value

class RealNumberNode(ASTNode):
    def __init__(self, token):
        self.raw_value = token.value

class ArrayLiteralNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class IdentifierNode(ASTNode):
    def __init__(self, token):
        self.name = token.value

class UnaryOpNode(ASTNode):
    def __init__(self, op_token, operand_expr):
        self.op = op_token.value
        self.operand = operand_expr

class BinaryOpNode(ASTNode):
    def __init__(self, left_expr, op_token, right_expr):
        self.left = left_expr
        self.op = op_token.value
        self.right = right_expr

class InputNode(ASTNode): # For '<'
    def __init__(self, var_name_token):
        self.var_name = var_name_token.value

class OutputCharNode(ASTNode): # For '>'
    def __init__(self, expr):
        self.expression = expr

class MultiCharOutputNode(ASTNode): # For '>> N' and '<< N'
    def __init__(self, type, count_expr):
        self.type = type # 'reversed' or 'normal'
        self.count = count_expr

class FunctionCallNode(ASTNode): # For '->> func_name args' and array functions
    def __init__(self, func_name_token, args):
        self.func_name = func_name_token.value
        self.args = args

class FunctionDefNode(ASTNode): # For '-> func_name args'
    def __init__(self, func_name_token, params, body_statements):
        self.func_name = func_name_token.value
        self.params = params # List of IdentifierNode for parameters
        self.body = body_statements

class ReturnNode(ASTNode): # For '^'
    def __init__(self, expr=None):
        self.expression = expr

class IfStatementNode(ASTNode): # For '?', '??#', '??:', '!'
    def __init__(self, condition, if_body, else_if_branches, else_body):
        self.condition = condition
        self.if_body = if_body
        self.else_if_branches = else_if_branches # List of (condition, body) tuples
        self.else_body = else_body

class WhileLoopNode(ASTNode): # For '@', '!@!'
    def __init__(self, condition, body_statements):
        self.condition = condition
        self.body = body_statements

class ForLoopNode(ASTNode): # For '#@#', '!@!'
    def __init__(self, iterator_var, range_expr, body_statements):
        self.iterator_var = iterator_var # IdentifierNode
        self.range_expr = range_expr # Expression that evaluates to an iterable (e.g., array)
        self.body = body_statements

class TryCatchNode(ASTNode): # For '%%', '%%%%'
    def __init__(self, try_body, catch_body, exception_var=None):
        self.try_body = try_body
        self.catch_body = catch_body
        self.exception_var = exception_var # IdentifierNode for exception variable

class ExceptionLiteralNode(ASTNode): # For '(exception_message)'
    def __init__(self, message_token):
        self.message = message_token.value[1:-1] # Remove parentheses

class Parser:
    """Builds an Abstract Syntax Tree (AST) from a stream of Tokens."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def _error(self, message):
        token = self.current_token()
        line = token.line if token else 'EOF'
        col = token.column if token else 'EOF'
        value = token.value if token else 'EOF'
        token_type = token.type if token else 'EOF'
        raise Exception(f"Parser Error at line {line}, col {col}: {message}. Got '{value}' ({token_type})")

    def current_token(self):
        """Returns the current token or None if end of tokens."""
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def peek_token(self, offset=1):
        """Peeks ahead without consuming tokens."""
        if self.current_token_index + offset < len(self.tokens):
            return self.tokens[self.current_token_index + offset]
        return None

    def advance(self):
        """Consumes the current token and moves to the next."""
        self.current_token_index += 1

    def eat(self, *expected_types):
        """Consumes the current token if its type matches one of the expected types."""
        token = self.current_token()
        if token and token.type in expected_types:
            self.advance()
            return token
        else:
            self._error(f"Expected one of {expected_types}, got {token.type if token else 'EOF'}")

    def parse_program(self):
        """Parses the entire MEL program."""
        self.eat('PROGRAM_START')
        statements = []
        while self.current_token() and self.current_token().type != 'PROGRAM_END':
            # Skip comments that might appear within the program body
            if self.current_token().type in ['COMMENT_SINGLE', 'COMMENT_PURE']:
                self.advance()
                continue
            statements.append(self.parse_statement())
        self.eat('PROGRAM_END')
        return ProgramNode(statements)

    def parse_statement(self):
        """Parses a single statement."""
        token = self.current_token()

        # Assignment
        if token and token.type == 'IDENTIFIER' and self.peek_token() and self.peek_token().type == 'ASSIGN':
            statement_node = self.parse_assignment()
        # Function Definition
        elif token and token.type == 'FUNCTION_DEF':
            statement_node = self.parse_function_definition()
        # Function Call / Array Function Call (can also be an expression)
        elif token and token.type == 'FUNCTION_CALL_PREFIX':
            statement_node = self.parse_function_call()
        # Output operations
        elif token and token.type == 'OUTPUT_CHAR':
            statement_node = self.parse_output_char()
        elif token and (token.type == 'OUTPUT_REVERSED' or token.type == 'OUTPUT_NORMAL'):
            statement_node = self.parse_multi_char_output()
        # Input operation
        elif token and token.type == 'INPUT':
            statement_node = self.parse_input()
        # Control Flow
        elif token and token.type == 'IF':
            statement_node = self.parse_if_statement()
        elif token and token.type == 'WHILE_LOOP':
            statement_node = self.parse_while_loop()
        elif token and token.type == 'FOR_LOOP':
            statement_node = self.parse_for_loop()
        elif token and token.type == 'TRY':
            statement_node = self.parse_try_catch()
        # Return statement
        elif token and token.type == 'RETURN':
            statement_node = self.parse_return()
        # Exception Literal (can appear as a statement if not part of a try/catch)
        elif token and token.type == 'LPAREN' and self.peek_token() and self.peek_token().type in ['IDENTIFIER', 'STRING'] and self.peek_token(2) and self.peek_token(2).type == 'RPAREN':
            statement_node = self.parse_exception_literal()
        else:
            self._error(f"Unexpected token for statement: '{token.value}' ({token.type})")
        
        # After parsing a statement, consume any inline comments on the same line.
        # This assumes statements are implicitly terminated by newlines or comments.
        # Check if the next token is on the same line and is a comment.
        while self.current_token() and self.current_token().line == token.line and \
              self.current_token().type in ['COMMENT_SINGLE', 'COMMENT_PURE']:
            self.advance()
            
        return statement_node

    def parse_assignment(self):
        """Parses an assignment statement: IDENTIFIER = EXPRESSION."""
        var_name_token = self.eat('IDENTIFIER')
        self.eat('ASSIGN')
        value_expr = self.parse_expression()
        return AssignmentNode(var_name_token, value_expr)

    def parse_expression(self):
        """
        Parses an expression, handling operator precedence.
        This is a simplified implementation for demonstration.
        A full parser would use a more robust precedence climbing algorithm.
        For now, it handles unary ops and then binary ops from left to right.
        """
        expr = self._parse_comparison_expression()
        return expr

    def _parse_comparison_expression(self):
        """Parses comparison expressions (lowest precedence)."""
        node = self._parse_arithmetic_expression()
        while self.current_token() and self.current_token().type in [
            'REAL_LT', 'REAL_EQ', 'REAL_GT', 'REAL_LE_EQ', 'REAL_GE_EQ', 'REAL_NE_EQ',
            'BINARY_LT', 'BINARY_EQ', 'BINARY_GT', 'BINARY_LE_EQ', 'BINARY_GE_EQ', 'BINARY_NE_EQ'
        ]:
            op_token = self.current_token()
            self.advance()
            right = self._parse_arithmetic_expression()
            node = BinaryOpNode(node, op_token, right)
        return node

    def _parse_arithmetic_expression(self):
        """Parses arithmetic expressions (higher precedence than comparison)."""
        node = self._parse_term() # Handles multiplication/division first
        while self.current_token() and self.current_token().type in [
            'REAL_ADD', 'REAL_SUB', 'BINARY_ADD', 'BINARY_SUB'
        ]:
            op_token = self.current_token()
            self.advance()
            right = self._parse_term()
            node = BinaryOpNode(node, op_token, right)
        return node

    def _parse_term(self):
        """Parses terms (multiplication, division, modulo, factorial, sqrt, power)."""
        node = self._parse_unary_expression()
        while self.current_token() and self.current_token().type in [
            'REAL_MUL', 'REAL_DIV', 'REAL_MOD', 'REAL_FACTORIAL', 'REAL_SQRT', 'REAL_POW',
            'BINARY_MUL', 'BINARY_DIV', 'BINARY_MOD', 'BINARY_FACTORIAL', 'BINARY_SQRT', 'BINARY_POW'
        ]:
            op_token = self.current_token()
            self.advance()
            # Factorial/Sqrt/Power are unary-like on the right, but here treated as binary for simplicity
            # A more robust parser would handle these as part of unary or post-fix ops
            if op_token.type in ['REAL_FACTORIAL', 'BINARY_FACTORIAL', 'REAL_SQRT', 'BINARY_SQRT', 'REAL_POW', 'BINARY_POW']:
                # For simplicity, these are treated as binary ops requiring a right operand.
                # In MEL, they are likely postfix unary, but current grammar treats them as infix binary.
                right = self._parse_unary_expression()
                node = BinaryOpNode(node, op_token, right)
            else:
                right = self._parse_unary_expression()
                node = BinaryOpNode(node, op_token, right)
        return node

    def _parse_unary_expression(self):
        """Parses unary expressions (e.g., |NUMBER)."""
        token = self.current_token()
        if token and token.type == 'UNARY_NEGATE':
            op_token = self.current_token()
            self.advance()
            operand = self._parse_primary_expression()
            return UnaryOpNode(op_token, operand)
        return self._parse_primary_expression()

    def _parse_primary_expression(self):
        """Parses basic literals, identifiers, or parenthesized expressions."""
        token = self.current_token()
        if token and token.type == 'STRING':
            self.eat('STRING')
            return StringLiteralNode(token)
        elif token and token.type == 'REAL_NUMBER':
            self.eat('REAL_NUMBER')
            return RealNumberNode(token)
        elif token and token.type.startswith('BINARY_'): # All binary literals
            # Handle multi-bit binary numbers: ;;$$$$$$$;$$$$$$$$
            if token.type == 'BINARY_LITERAL_PREFIX':
                self.eat('BINARY_LITERAL_PREFIX') # Consume ';;'
                bit_sequence_tokens = []
                while self.current_token() and self.current_token().type in ['BINARY_BIT_ZERO', 'BINARY_BIT_ONE']:
                    bit_sequence_tokens.append(self.eat(self.current_token().type))
                    if self.current_token() and self.current_token().type == 'SEMICOLON_DELIMITER':
                        self.eat('SEMICOLON_DELIMITER') # Consume semicolon
                return BinaryLiteralNode(';;' + ';'.join([t.value for t in bit_sequence_tokens]))
            else: # All other single binary literals ($$, $$$, etc.)
                self.eat(token.type) # Consume the specific binary token
                return BinaryLiteralNode(token.value)
        elif token and token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            return IdentifierNode(token)
        elif token and token.type == 'ARRAY_START':
            return self.parse_array_literal()
        elif token and token.type == 'LPAREN':
            # Check if it's an exception literal or a parenthesized expression
            # Exception literal: (IDENTIFIER) or (STRING)
            if self.peek_token() and self.peek_token().type in ['IDENTIFIER', 'STRING'] and \
               self.peek_token(2) and self.peek_token(2).type == 'RPAREN':
                return self.parse_exception_literal()
            else: # Standard parenthesized expression
                self.eat('LPAREN')
                expr = self.parse_expression()
                self.eat('RPAREN')
                return expr
        elif token and token.type == 'FUNCTION_CALL_PREFIX': # Added this case for function calls as expressions
            return self.parse_function_call()
        else:
            self._error(f"Unexpected token for primary expression: '{token.value}' ({token.type})")

    def parse_array_literal(self):
        """Parses an array literal: [item1, item2, ...] (using [ and ])."""
        self.eat('ARRAY_START')
        elements = []
        if self.current_token() and self.current_token().type != 'ARRAY_END':
            elements.append(self.parse_expression())
            while self.current_token() and self.current_token().type == 'COMMA':
                self.eat('COMMA')
                elements.append(self.parse_expression())
        self.eat('ARRAY_END')
        return ArrayLiteralNode(elements)

    def parse_input(self):
        """Parses an input statement: < IDENTIFIER."""
        self.eat('INPUT')
        var_name_token = self.eat('IDENTIFIER')
        return InputNode(var_name_token)

    def parse_output_char(self):
        """Parses single character output: > EXPRESSION."""
        self.eat('OUTPUT_CHAR')
        expr = self.parse_expression()
        return OutputCharNode(expr)

    def parse_multi_char_output(self):
        """Parses multi-character output: >> N or << N."""
        output_type_token = self.eat('OUTPUT_REVERSED', 'OUTPUT_NORMAL')
        expr = self.parse_expression() # This should be the count
        return MultiCharOutputNode(output_type_token.type, expr)

    def parse_function_call(self):
        """Parses a function call: ->> IDENTIFIER args... or ->> : args..."""
        self.eat('FUNCTION_CALL_PREFIX')
        func_name_token = None
        # Special handling for '->> :' (eval-like functionality)
        if self.current_token() and self.current_token().type == 'COLON':
            func_name_token = self.eat('COLON') # Consume the ':' token
        else:
            func_name_token = self.eat('IDENTIFIER') # Regular function name
        
        args = []
        # Arguments are space-separated expressions until end of line or next statement
        # This is a heuristic and might need refinement for complex cases
        # Stop at tokens that are clearly not part of an expression or are statement delimiters
        expression_end_tokens = [
            'PROGRAM_END', 'COMMENT_SINGLE', 'COMMENT_PURE',
            'ASSIGN', 'INPUT', 'OUTPUT_CHAR', 'OUTPUT_REVERSED', 'OUTPUT_NORMAL',
            'FUNCTION_DEF', 'FUNCTION_CALL_PREFIX', 'RETURN', 'TRY',
            'IF', 'ELSE_IF', 'ELSE', 'END_CONDITIONAL',
            'WHILE_LOOP', 'FOR_LOOP', 'END_LOOP', 'CATCH',
            'COMMA', 'SEMICOLON_DELIMITER', 'RPAREN', 'ARRAY_END', 'ARRAY_START', 'LPAREN', 'COLON' 
        ]
        
        while self.current_token() and self.current_token().type not in expression_end_tokens:
            try:
                arg_expr = self.parse_expression()
                args.append(arg_expr)
            except Exception as e:
                # If it's a parser error that means the current token is not an expression part,
                # then we stop collecting arguments.
                if "Parser Error" in str(e):
                    break
                else:
                    raise # Re-raise other exceptions
        return FunctionCallNode(func_name_token, args)

    def parse_function_definition(self):
        """Parses a function definition: -> IDENTIFIER args BODY."""
        self.eat('FUNCTION_DEF')
        func_name_token = self.eat('IDENTIFIER')
        params = []
        # Parameters are identifiers, space-separated
        while self.current_token() and self.current_token().type == 'IDENTIFIER':
            params.append(IdentifierNode(self.eat('IDENTIFIER')))

        # Function body is a block of statements.
        # It ends at a RETURN, another FUNCTION_DEF, or PROGRAM_END.
        body_statements = self._parse_block(
            end_tokens=['RETURN', 'FUNCTION_DEF', 'PROGRAM_END', 'IF', 'WHILE_LOOP', 'FOR_LOOP', 'TRY', 'CATCH'] 
        )
        
        return FunctionDefNode(func_name_token, params, body_statements)

    def parse_return(self):
        """Parses a return statement: ^ [EXPRESSION]."""
        self.eat('RETURN')
        expr = None
        # Check if there's an expression after '^'
        # A return expression can be followed by comments or end of program
        if self.current_token() and self.current_token().type not in ['PROGRAM_END', 'COMMENT_SINGLE', 'COMMENT_PURE']:
            try:
                expr = self.parse_expression()
            except Exception:
                pass # No expression, just a bare return
        return ReturnNode(expr)

    def parse_if_statement(self):
        """Parses an If-Else If-Else block."""
        self.eat('IF')
        condition = self.parse_expression()
        if_body = self._parse_block(
            # Removed 'IF' from end_tokens for if_body, as it should be a new statement
            end_tokens=['END_CONDITIONAL', 'ELSE_IF', 'ELSE', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'WHILE_LOOP', 'FOR_LOOP', 'CATCH'] 
        )
        
        else_if_branches = []
        while self.current_token() and self.current_token().type == 'ELSE_IF':
            self.eat('ELSE_IF')
            else_if_condition = self.parse_expression()
            else_if_body = self._parse_block(
                # Removed 'IF' from end_tokens for else_if_body
                end_tokens=['END_CONDITIONAL', 'ELSE_IF', 'ELSE', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'WHILE_LOOP', 'FOR_LOOP', 'CATCH']
            )
            else_if_branches.append((else_if_condition, else_if_body))
            
        else_body = None
        if self.current_token() and self.current_token().type == 'ELSE':
            self.eat('ELSE')
            else_body = self._parse_block(
                # Removed 'IF' from end_tokens for else_body
                end_tokens=['END_CONDITIONAL', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'WHILE_LOOP', 'FOR_LOOP', 'CATCH']
            )
            
        self.eat('END_CONDITIONAL')
        return IfStatementNode(condition, if_body, else_if_branches, else_body)

    def _parse_block(self, end_tokens=None):
        """
        Helper to parse a block of statements until a specific end token.
        This is crucial for control flow (if, loops, try/catch) and functions.
        It stops at tokens that mark the end of a block or the start of a new top-level construct.
        """
        if end_tokens is None:
            # Default end tokens for general blocks (e.g., top-level statements)
            end_tokens = ['PROGRAM_END'] 
        
        block_statements = []
        while self.current_token() and self.current_token().type not in end_tokens:
            # Skip comments within blocks
            if self.current_token().type in ['COMMENT_SINGLE', 'COMMENT_PURE']:
                self.advance()
                continue
            
            # If we hit PROGRAM_END, it's an error if it's not in end_tokens for this block
            if self.current_token().type == 'PROGRAM_END' and 'PROGRAM_END' not in end_tokens:
                self._error("Unexpected end of program within a block.")

            # Attempt to parse a statement. If it fails, it might be an unexpected token
            # that's not explicitly in end_tokens, or a malformed statement.
            try:
                statement = self.parse_statement()
                block_statements.append(statement)
            except Exception as e:
                # If the error is not due to hitting an end_token, then it's a real syntax error
                if self.current_token() and self.current_token().type not in end_tokens:
                    self._error(f"Error parsing block statement: {e}")
                else:
                    # We hit an end_token, so we break the loop. This is expected.
                    break
        return block_statements

    def parse_while_loop(self):
        """Parses a While loop: @ CONDITION BODY !@!."""
        self.eat('WHILE_LOOP')
        condition = self.parse_expression()
        body = self._parse_block(
            end_tokens=['END_LOOP', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'IF', 'WHILE_LOOP', 'FOR_LOOP', 'CATCH']
        )
        self.eat('END_LOOP')
        return WhileLoopNode(condition, body)

    def parse_for_loop(self):
        """Parses a For loop: #@# IDENTIFIER EXPRESSION BODY !@!."""
        self.eat('FOR_LOOP')
        iterator_var = self.eat('IDENTIFIER')
        range_expr = self.parse_expression() # This should evaluate to an array
        body = self._parse_block(
            end_tokens=['END_LOOP', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'IF', 'WHILE_LOOP', 'FOR_LOOP', 'CATCH']
        )
        self.eat('END_LOOP')
        return ForLoopNode(IdentifierNode(iterator_var), range_expr, body)

    def parse_try_catch(self):
        """Parses a Try-Catch block: %% BODY %%%% [IDENTIFIER] BODY."""
        self.eat('TRY')
        try_body = self._parse_block(
            end_tokens=['CATCH', 'PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'IF', 'WHILE_LOOP', 'FOR_LOOP']
        )
        self.eat('CATCH')
        
        exception_var = None # Not explicitly supported in MEL syntax for now
        
        catch_body = self._parse_block(
            end_tokens=['PROGRAM_END', 'FUNCTION_DEF', 'RETURN', 'TRY', 'IF', 'WHILE_LOOP', 'FOR_LOOP']
        )
        return TryCatchNode(try_body, catch_body, exception_var)

    def parse_exception_literal(self):
        """Parses an exception literal: (exception_message)."""
        self.eat('LPAREN')
        # Message can be an identifier or a string literal
        message_token = self.eat('IDENTIFIER', 'STRING')
        self.eat('RPAREN')
        return ExceptionLiteralNode(message_token)

    def parse(self):
        """Starts the parsing process."""
        return self.parse_program()

# --- 3. Interpreter (Execution) ---

class MELRuntimeError(Exception):
    """Custom exception for MEL runtime errors."""
    pass

class Environment:
    """Manages variable scopes."""
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        """Defines a new variable in the current scope."""
        self.values[name] = value

    def assign(self, name, value):
        """Assigns a value to an existing variable, searching up the scope chain."""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise MELRuntimeError(f"Undefined variable '{name}'")

    def get(self, name):
        """Retrieves a variable's value, searching up the scope chain."""
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise MELRuntimeError(f"Undefined variable '{name}'")

class Interpreter:
    """Executes the MEL Abstract Syntax Tree."""
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.output_buffer = [] # Stores recently printed characters for >> and <<
        self.functions = {} # Stores defined functions: {name: FunctionDefNode}

    def _visit(self, node):
        """Dispatches to the appropriate visit method based on node type."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node):
        raise MELRuntimeError(f"No visit method for node type: {type(node).__name__}")

    def interpret(self, ast):
        """Starts the interpretation process from the root AST node."""
        self._visit(ast)

    def visit_ProgramNode(self, node):
        for statement in node.statements:
            self._visit(statement)

    def visit_AssignmentNode(self, node):
        value = self._visit(node.value_expr)
        self.current_env.define(node.var_name, value)

    def visit_StringLiteralNode(self, node):
        return node.value

    def visit_BinaryLiteralNode(self, node):
        raw_value = node.raw_value
        if raw_value == '$$': return False
        if raw_value == '$$$': return True
        if raw_value == '$$$$': return None
        if raw_value == '$$$$$': return [] # Represents "empty, non-existent" as an empty list/array
        if raw_value == '$$$$$$': return 0
        if raw_value == '$$$$$$$': return 0 # Single binary 0
        if raw_value == '$$$$$$$$': return 1 # Single binary 1
        
        # Handle multi-bit binary numbers: ;;$$$$$$$;$$$$$$$$
        if raw_value.startswith(';;'):
            # Reconstruct the bit string from raw_value (e.g., ';;$$$$$$$$;$$$$$$$')
            # Split by ';' and map to '0' or '1'
            bit_parts = raw_value[2:].split(';')
            bits = ''.join(['0' if b == '$$$$$$$' else '1' for b in bit_parts if b]) # Filter empty strings from split
            if not bits: # Handle cases like `;;`
                return 0
            return int(bits, 2)
        
        raise MELRuntimeError(f"Unknown binary literal: {raw_value}")

    def visit_RealNumberNode(self, node):
        parts = node.raw_value.split(":")
        # Convert # to digit length, then join for float
        digits = [str(len(part)) for part in parts]
        return float(".".join([digits[0]] + digits[1:]))

    def visit_ArrayLiteralNode(self, node):
        return [self._visit(elem) for elem in node.elements]

    def visit_IdentifierNode(self, node):
        return self.current_env.get(node.name)

    def visit_UnaryOpNode(self, node):
        operand_val = self._visit(node.operand)
        if node.op == '|': # Negate number
            if isinstance(operand_val, (int, float)):
                return -operand_val
            raise MELRuntimeError(f"Unary negate operator '|' expects a number, got {type(operand_val)}")
        raise MELRuntimeError(f"Unknown unary operator: {node.op}")

    def visit_BinaryOpNode(self, node):
        left_val = self._visit(node.left)
        right_val = self._visit(node.right)
        op = node.op

        # Helper for type checking
        def check_types(l, r, expected_type_str):
            if not isinstance(l, (int, float)) or not isinstance(r, (int, float)):
                raise MELRuntimeError(f"Binary operator '{op}' expects {expected_type_str} numbers, got {type(l)} and {type(r)}")

        if op.startswith('$'): # Binary operators
            check_types(left_val, right_val, "binary")
            if not isinstance(left_val, int) or not isinstance(right_val, int):
                raise MELRuntimeError(f"Binary operator '{op}' expects integers, got {type(left_val)} and {type(right_val)}")

            if op == '$+': return left_val + right_val
            if op == '$-': return left_val - right_val
            if op == '$*': return left_val * right_val
            if op == '$/':
                if right_val == 0: raise MELRuntimeError("( $$$$$$/$$$$$$ ) Binary division by zero")
                return left_val // right_val # Integer division for binary
            if op == '$!': # Factorial (right_val is ignored, it's unary-like)
                if left_val < 0: raise MELRuntimeError("( |#...#! ) Binary factorial of negative number")
                res = 1
                for i in range(1, left_val + 1): res *= i
                return res
            if op == '$\\': # Square root (right_val is ignored, it's unary-like)
                if left_val < 0: raise MELRuntimeError("( #\\|#... ) Binary square root of negative number")
                return int(left_val**0.5) # Integer result for binary sqrt
            if op == '$%':
                if right_val == 0: raise MELRuntimeError("Binary modulo by zero")
                return left_val % right_val
            if op == '$^': return left_val ** right_val
            
            # Binary Comparison
            if op == '$<': return left_val < right_val
            if op == '$=': return left_val == right_val
            if op == '$>': return left_val > right_val
            if op == '$<=': return left_val <= right_val
            if op == '$>=': return left_val >= right_val
            if op == '$!=': return left_val != right_val

        elif op.startswith('#'): # Real operators
            check_types(left_val, right_val, "real")

            if op == '#+': return left_val + right_val
            if op == '#-': return left_val - right_val
            if op == '#*': return left_val * right_val
            if op == '#/':
                if right_val == 0: raise MELRuntimeError("( $$$$$$/$$$$$$ ) Real division by zero")
                return left_val / right_val # Float division for real
            if op == '#!': # Factorial (right_val is ignored, it's unary-like)
                if left_val < 0: raise MELRuntimeError("( |#...#! ) Real factorial of negative number")
                # Factorial for floats is complex (Gamma function). For simplicity, only integer part.
                res = 1.0
                for i in range(1, int(left_val) + 1): res *= i
                return res
            if op == '#\\': # Square root (right_val is ignored, it's unary-like)
                if left_val < 0: raise MELRuntimeError("( #\\|#... ) Real square root of negative number")
                return left_val**0.5
            if op == '#%':
                if right_val == 0: raise MELRuntimeError("Real modulo by zero")
                return left_val % right_val
            if op == '#^': return left_val ** right_val

            # Real Comparison
            if op == '#<': return left_val < right_val
            if op == '#=': return left_val == right_val
            if op == '#>': return left_val > right_val
            if op == '#<=': return left_val <= right_val
            if op == '#>=': return left_val >= right_val
            if op == '#!=': return left_val != right_val

        raise MELRuntimeError(f"Unknown binary operator: {op}")

    def visit_InputNode(self, node):
        input_value = input(f"Enter value for '{node.var_name}': ")
        self.current_env.assign(node.var_name, input_value) # Store as string, conversion handled by eval_expr if needed

    def visit_OutputCharNode(self, node):
        value = self._visit(node.expression)
        if isinstance(value, str) and len(value) > 0:
            char_to_print = value[0] # Confirmed: prints only the first character
        elif isinstance(value, (int, float)):
            # Convert number to character (e.g., ASCII)
            try:
                char_to_print = chr(int(value))
            except ValueError:
                raise MELRuntimeError(f"Cannot convert number {value} to a character (out of ASCII range).")
        else:
            # For booleans, None, etc., convert to string and take first char
            char_to_print = str(value)[0] if len(str(value)) > 0 else ''

        self.output_buffer.append(char_to_print)
        print(char_to_print, end="")

    def visit_MultiCharOutputNode(self, node):
        count = self._visit(node.count)
        if not isinstance(count, int) or count < 0:
            raise MELRuntimeError(f"Multi-character output count must be a non-negative integer, got {count}")
        
        if count > len(self.output_buffer):
            raise MELRuntimeError(f"Cannot retrieve {count} characters, only {len(self.output_buffer)} available in buffer.")

        chars_to_print = self.output_buffer[-count:]
        if node.type == 'OUTPUT_REVERSED': # >> N
            print("".join(reversed(chars_to_print)), end="")
        else: # << N
            print("".join(chars_to_print), end="")
        
        # Clear printed characters from buffer
        self.output_buffer = self.output_buffer[:-count]

    def visit_FunctionCallNode(self, node):
        func_name = node.func_name
        args_values = [self._visit(arg) for arg in node.args]

        # Handle built-in array/string functions
        if func_name == 'append':
            if len(args_values) < 2: raise MELRuntimeError("append requires at least array_variable_name and one item")
            array_var_name = args_values[0] # Assuming first arg is variable name string
            if not isinstance(array_var_name, str): raise MELRuntimeError("append: first argument must be array variable name (string)")
            
            array = self.current_env.get(array_var_name)
            if not isinstance(array, list): raise MELRuntimeError(f"append: '{array_var_name}' is not an array")
            
            array.extend(args_values[1:])
            self.current_env.assign(array_var_name, array) # Update the array in scope
            return None
        elif func_name == 'length':
            if len(args_values) != 1: raise MELRuntimeError("length requires one argument")
            val = args_values[0]
            if isinstance(val, (str, list)):
                return len(val)
            raise MELRuntimeError(f"length expects string or array, got {type(val)}")
        elif func_name == 'getitem':
            if len(args_values) != 2: raise MELRuntimeError("getitem requires two arguments: array/string and index")
            collection = args_values[0]
            index = args_values[1]
            if not isinstance(index, int): raise MELRuntimeError("getitem index must be an integer")
            if not isinstance(collection, (str, list)): raise MELRuntimeError("getitem expects string or array")
            if not (1 <= index <= len(collection)): raise MELRuntimeError("getitem index out of bounds (1-based)")
            return collection[index - 1] # MEL is 1-based indexing
        elif func_name == 'list':
            if len(args_values) != 1: raise MELRuntimeError("list requires one argument")
            val = args_values[0]
            if isinstance(val, (str, list)):
                print(val, end="") # Prints the Python representation of the list/string
            else:
                raise MELRuntimeError(f"list expects string or array, got {type(val)}")
            return None
        elif func_name == 'reverse':
            if len(args_values) != 1: raise MELRuntimeError("reverse requires one argument")
            val = args_values[0]
            if isinstance(val, str):
                return val[::-1]
            elif isinstance(val, list):
                return val[::-1] # Returns a new reversed list
            raise MELRuntimeError(f"reverse expects string or array, got {type(val)}")
        elif func_name == ':': # Special case for `->> : Run MEL string code`
            if len(args_values) != 1 or not isinstance(args_values[0], str):
                raise MELRuntimeError("Run MEL string code (->> :) expects a single string argument.")
            
            embedded_code = args_values[0]
            try:
                # Create a new lexer/parser/interpreter for the embedded code
                # This will run in its own isolated environment (global scope)
                sub_lexer = Lexer(embedded_code)
                sub_tokens = sub_lexer.get_tokens()
                sub_parser = Parser(sub_tokens)
                sub_ast = sub_parser.parse()
                
                sub_interpreter = Interpreter()
                sub_interpreter.interpret(sub_ast)
                return None
            except Exception as e:
                raise MELRuntimeError(f"Error in embedded MEL code: {e}")
        
        # Handle user-defined functions
        if func_name not in self.functions:
            raise MELRuntimeError(f"Undefined function '{func_name}'")
        
        func_def_node = self.functions[func_name]
        if len(args_values) != len(func_def_node.params):
            raise MELRuntimeError(f"Function '{func_name}' expects {len(func_def_node.params)} arguments, got {len(args_values)}")
        
        # Create a new scope for the function call
        previous_env = self.current_env
        self.current_env = Environment(previous_env)
        
        # Bind arguments to parameters in the new scope
        for i, param_node in enumerate(func_def_node.params):
            self.current_env.define(param_node.name, args_values[i])
            
        return_value = None
        try:
            # Execute function body statements
            for statement in func_def_node.body:
                self._visit(statement)
        except ReturnValue as rv: # Catch custom return exception
            return_value = rv.value
        except Exception as e: # Catch any other unexpected Python errors during function body execution
            raise MELRuntimeError(f"Python error during function '{func_name}' execution: {e}") from e
        finally:
            self.current_env = previous_env # Restore previous scope
        
        return return_value

    def visit_FunctionDefNode(self, node):
        # Store the function definition node. The parser has already collected its body.
        self.functions[node.func_name] = node

    def visit_ReturnNode(self, node):
        value = self._visit(node.expression) if node.expression else None
        raise ReturnValue(value) # Use a custom exception for non-local exits

    def visit_IfStatementNode(self, node):
        condition_result = self._visit(node.condition)
        if condition_result:
            for stmt in node.if_body:
                self._visit(stmt)
        else:
            found_else_if = False
            for cond, body in node.else_if_branches:
                if self._visit(cond):
                    for stmt in body:
                        self._visit(stmt)
                    found_else_if = True
                    break
            if not found_else_if and node.else_body:
                for stmt in node.else_body:
                    self._visit(stmt)

    def visit_WhileLoopNode(self, node):
        while self._visit(node.condition):
            for stmt in node.body:
                self._visit(stmt)

    def visit_ForLoopNode(self, node):
        iterable = self._visit(node.range_expr)
        if not isinstance(iterable, list):
            raise MELRuntimeError(f"For loop range expression must be an array, got {type(iterable)}")
        
        previous_env = self.current_env
        self.current_env = Environment(previous_env) # New scope for loop variable
        
        for item in iterable:
            self.current_env.define(node.iterator_var.name, item)
            for stmt in node.body:
                self._visit(stmt)
        
        self.current_env = previous_env # Restore scope

    def visit_TryCatchNode(self, node):
        try:
            for stmt in node.try_body:
                self._visit(stmt)
        except MELRuntimeError as e:
            # If `exception_var` was specified in the AST, we'd assign `e.message` to it.
            # For now, just execute the catch body.
            for stmt in node.catch_body:
                self._visit(stmt)
        except Exception as e: # Catch any unexpected Python errors during try block execution
            for stmt in node.catch_body:
                self._visit(stmt)

    def visit_ExceptionLiteralNode(self, node):
        # When an exception literal is evaluated, it means it's being thrown.
        raise MELRuntimeError(node.message)

class ReturnValue(Exception):
    """Custom exception for handling function returns (non-local exit)."""
    def __init__(self, value):
        self.value = value

# --- Main Runner Function ---

def run_mel_code(code_string):
    """
    Parses and interprets the given MEL code string.
    """
    print("--- MEL Interpreter Output ---")
    try:
        # 1. Lexing
        lexer = Lexer(code_string)
        tokens = lexer.get_tokens()

        # 2. Parsing
        parser = Parser(tokens)
        ast = parser.parse()

        # 3. Interpretation
        interpreter = Interpreter()
        interpreter.interpret(ast)

    except MELRuntimeError as e:
        print(f"\nMEL Runtime Error: {e}")
    except ReturnValue as e: # Catch ReturnValue specifically to suppress traceback
        # print(f"\nFunction returned: {e.value}") # Optional: for debugging returns
        pass # Suppress traceback for normal function returns
    except Exception as e:
        print(f"\nInternal Interpreter Error: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for unexpected errors
    print("--- Interpretation Finished ---")

# --- Sample MEL Code ---

# Example 1: Basic Assignment and Output (Adjusted for single-char output)
sample_code_1 = """
::: Program start
myString = "Hello, Muser!"
> "H"
> "e"
> "l"
> "l"
> "o"
> ","
> " "
> "M"
> "u"
> "s"
> "e"
> "r"
> "!"
;;; Program end
"""

# Example 2: Numbers and Arithmetic (Fixed token precedence and added comments for ASCII output)
sample_code_2 = """
::: Program start
num_binary_1 = ;;$$$$$$$$;$$$$$$$ ~ Binary 11 (decimal 3)
num_binary_2 = $$$$$$$$ ~ Binary 1 (decimal 1)
sum_binary = num_binary_1 $+ num_binary_2
> sum_binary ~ Prints ASCII char for 4 (EOT)

real_num_1 = ###:#:#### ~ 3.14
real_num_2 = #:# ~ 1.0
sum_real = real_num_1 #+ real_num_2
> sum_real ~ Prints ASCII char for 4 (EOT) (3.14 + 1.0 = 4.14, int(4.14) = 4)

product_real = real_num_1 #* real_num_2
> product_real ~ Prints ASCII char for 3 (ETX) (3.14 * 1.0 = 3.14, int(3.14) = 3)

neg_num = |##### ~ -5
> neg_num ~ Prints ASCII char for 251 (negative values wrap around byte for chr())

;;; Program end
"""

# Example 3: Arrays and Array Functions (Fixed array literal syntax from `` to [])
sample_code_3 = """
::: Program start
fruits = ["apple", "banana"]
->> append fruits "cherry" "grape"
->> list fruits ~ Should print ['apple', 'banana', 'cherry', 'grape']

len_fruits = ->> length fruits
> len_fruits ~ Prints ASCII char for 4 (length of array)

first_fruit = ->> getitem fruits $$$$$$$$ ~ Index 1 (binary 1)
> first_fruit ~ Prints 'a'

reversed_fruits = ->> reverse fruits
->> list reversed_fruits ~ Should print ['grape', 'cherry', 'banana', 'apple']

;;; Program end
"""

# Example 4: Output Buffer (>> and <<) (Parser fixed for expressions)
sample_code_4 = """
::: Program start
> "A"
> "B"
> "C"
> "D"
>> $$$ ~ Prints "CBA" (reversed last 3 from buffer)
<< $$$ ~ Prints "D" (last 1 from remaining buffer)
;;; Program end
"""

# Example 5: Conditionals (Fixed token precedence and block parsing)
sample_code_5 = """
::: Program start
myVar = $$$$$$ ~ 0 (decimal 0)
? myVar $= $$$$$$ ~ If myVar is 0
    > "Z"
!
myVar2 = $$$$$$$$ ~ 1 (binary 1)
? myVar2 $= $$$$$$ ~ If myVar2 is 0 (false)
    > "X"
??: ~ Else
    > "Y"
!
;;; Program end
"""

# Example 6: Loops (Fixed token precedence and block parsing)
sample_code_6 = """
::: Program start
counter = $$$$$$ ~ 0
@ counter $< $$$$$$$$ ~ While counter < 1 (binary 1)
    > "L"
    counter = counter $+ $$$$$$$$ ~ counter = counter + 1
!@!
;;; Program end
"""

# Example 7: Try-Catch (Adjusted to trigger a division by zero error, fixed token precedence)
sample_code_7 = """
::: Program start
%%
    error_val = $$$$$$/$$$$$$ ~ This should cause 0/0 error (binary 0 / binary 0)
    > "This should not print"
%%%%
    > "Caught an error!"
;;; Program end
"""

# Example 8: User-defined function (Function body parsing fixed, improved error handling)
sample_code_8 = """
::: Program start
-> greet name
    > "H"
    > "i"
    > ","
    > " "
    > name
    ^ ~ Return from function (implicitly returns None if no expression)
->> greet "Alice"
->> greet "Bob"
;;; Program end
"""

# Example 9: Eval-like functionality (->> : Run MEL string code) (Fixed colon token parsing)
sample_code_9 = """
::: Program start
code_to_run = "::: Program start\\n> \\"E\\"> \\"V\\"> \\"A\\"> \\"L\\"\\n;;; Program end"
->> : code_to_run
;;; Program end
"""

# --- Run the samples ---
if __name__ == "__main__":
    print("\n--- Running Sample 1 (Basic Assignment and Output) ---")
    run_mel_code(sample_code_1)

    print("\n\n--- Running Sample 2 (Numbers and Arithmetic) ---")
    run_mel_code(sample_code_2)

    print("\n\n--- Running Sample 3 (Arrays and Array Functions) ---")
    run_mel_code(sample_code_3)

    print("\n\n--- Running Sample 4 (Output Buffer) ---")
    run_mel_code(sample_code_4)

    print("\n\n--- Running Sample 5 (Conditionals) ---")
    run_mel_code(sample_code_5)

    print("\n\n--- Running Sample 6 (Loops) ---")
    run_mel_code(sample_code_6)

    print("\n\n--- Running Sample 7 (Try-Catch) ---")
    run_mel_code(sample_code_7)
    
    print("\n\n--- Running Sample 8 (User-defined function) ---")
    run_mel_code(sample_code_8)

    print("\n\n--- Running Sample 9 (Eval-like functionality) ---")
    run_mel_code(sample_code_9)

