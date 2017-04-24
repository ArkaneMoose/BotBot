import re
import random
import sys
import traceback
import ast
import operator
import time
import json
from simpleeval import SimpleEval, DEFAULT_OPERATORS, DEFAULT_FUNCTIONS, DEFAULT_NAMES
from botbot.euphutils import EuphUtils

import botbot.logger as logger

log = logger.Logger()

# functions and operators that can be used in ${math} syntax
EVAL_FUNCTIONS = DEFAULT_FUNCTIONS.copy()
EVAL_FUNCTIONS.update({'bool': bool, 'repr': repr, 'to_json': lambda x: json.dumps(x), 'from_json': lambda x: json.loads(x), 'len': len, 'mention': EuphUtils.mention, 'unwhitespace': lambda x: re.sub(r'\s', '_', x), 'time': time.time, 'eval': None})
EVAL_OPERATORS = DEFAULT_OPERATORS.copy()
EVAL_OPERATORS.update({ast.Not: operator.not_, ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b, ast.Is: operator.is_, ast.IsNot: operator.is_not})

class Parser:
    def __init__(self, parse_string, dbginfo=None):
        temp = ''
        self.array = []
        self.parse_string = parse_string
        self.dbginfo = dbginfo or 'N/A'
        self.variables = {}
        regex_mode = True
        i = 0
        while i < len(parse_string) and re.match(r'\s', parse_string[i]):
            i += 1
        while i < len(parse_string):
            if regex_mode:
                arrow_match = re.match(r'\s*->\s*', parse_string[i:])
                if arrow_match:
                    i += len(arrow_match.group(0))
                    regex_mode = False
                    if i >= len(parse_string):
                        self.array.append([temp, [0, '']])
                    else:
                        self.array.append([temp])
                    temp = ''
                else:
                    temp += parse_string[i]
                    i += 1
            else:
                temp = self.parse_response_string(parse_string[i:])
                self.array[-1].append(temp[0])
                i += len(temp[1])
                temp = ''
                whitespace_match = re.match('\s*', parse_string[i:])
                if whitespace_match:
                    i += len(whitespace_match.group(0))
                regex_mode = True

    def load_array(self, array):
        self.array = array

    def get_messages(self, content, sender):
        for entry in self.array:
            raw_regex_string = entry[0]
            regex_string = ''
            i = 0
            while i < len(raw_regex_string):
                if raw_regex_string[i:].startswith('${'):
                    i += 2
                    # parse the variable name as if it was part of a response
                    parsed = self.parse_response_string(raw_regex_string[i:], 3)
                    i += len(parsed[1])
                    variable = next(self.parse_entry(parsed[0]), '')
                    regex_string += re.escape(variable)
                else:
                    regex_string += raw_regex_string[i]
                    i += 1
            try:
                regex = re.compile(regex_string, re.IGNORECASE)
            except re.error as e:
                log.write('Bad regular expression {!r} ({!s}), ignoring. ({!s})'.format(regex_string, e.message, self.dbginfo))
                continue
            match = regex.search(content)
            if match:
                messages = self.parse_entry(entry[1])
                self.variables['groups'] = list(match.groups())
                self.variables['groups'].insert(0, match.group(0))
                groups = tuple(reversed(match.groups('')))
                groups = tuple(zip(map('\\{0}'.format, range(len(groups), 0, -1)), groups))
                for message in messages:
                    for backreference, group in groups:
                        message = message.replace(backreference, group)
                    yield message

    def get_regexes(self):
        return list(map(lambda entry: entry[0], self.array))

    def parse_entry(self, parsed_data):
        if parsed_data[0] == 0: # concatenation
            if len(parsed_data) == 1:
                return
            element = parsed_data[1]
            remainder = parsed_data[2:]
            remainder.insert(0, 0)
            if type(element) is str:
                result = None
                for result in self.parse_entry(remainder):
                    yield element + result
                if result is None:
                    yield element
            else:
                element_result = None
                for element_result in self.parse_entry(element):
                    remainder_result = None
                    for remainder_result in self.parse_entry(remainder):
                        yield element_result + remainder_result
                    if remainder_result is None:
                        yield element_result
                if element_result is None:
                    for remainder_result in self.parse_entry(remainder):
                        yield remainder_result
        elif parsed_data[0] == 1: # random choice [a,b,c]
            element = parsed_data[random.randint(1, len(parsed_data) - 1)]
            if type(element) is not str:
                for result in self.parse_entry(element):
                    yield result
            else:
                yield element
        elif parsed_data[0] == 2: # multiple response {a,b,c}
            for element in parsed_data[1:]:
                if type(element) is str:
                    yield element
                else:
                    for result in self.parse_entry(element):
                        yield result
        elif parsed_data[0] == 3: # dynamic variable ${variable}
            variable_name = parsed_data[1]
            if type(variable_name) is not str:
                variable_name = next(self.parse_entry(variable_name), '')
            evaluator = SimpleEval(names=self.variables.copy(), functions=EVAL_FUNCTIONS, operators=EVAL_OPERATORS)
            evaluator.names['variables'] = evaluator.names
            evaluator.functions['eval'] = evaluator.eval
            try:
                yield str(evaluator.eval(variable_name))
            except GeneratorExit:
                pass
            except:
                yield '[Error: {0}]'.format(''.join(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1])).strip())

    def parse_response_string(self, data, datatype=0):
        parsed = [datatype]

        # possible expression types:
        # 0 = concatenation
        # 1 = random choice [a,b,c]
        # 2 = multiple response {a,b,c}
        # 3 = dynamic variable ${variable}
        start = {'[': 1, '{': 2, '${': 3}
        end = {0: ';', 1: ']', 2: '}', 3: '}'}

        startchars = tuple(start.keys())
        endchar = end[datatype]
        i = 0
        separate = True
        separatable = {0: False, 1: True, 2: True, 3: False}[datatype]
        allow_nesting = {0: True, 1: True, 2: True, 3: False}[datatype]
        while i < len(data):
            if separate and re.match(r'\s', data[i]):
                i += 1
                continue
            elif data[i] == endchar:
                if separate:
                    parsed.append('')
                return (parsed, data[:i + 1])
            elif allow_nesting and data[i:].startswith(startchars):
                startchar = next(char for char in startchars if data[i:].startswith(char))
                expression_type = start[startchar]
                i += len(startchar)
                subparsed = self.parse_response_string(data[i:], expression_type)
                i += len(subparsed[1])
                if separate or parsed[0] == 0:
                    parsed.append(subparsed[0])
                    separate = False
                else:
                    if type(parsed[-1]) is list and parsed[-1][0] == 0:
                        parsed[-1].append(subparsed[0])
                    else:
                        parsed[-1] = [0, parsed[-1], subparsed[0]]
                continue
            elif separatable and data[i] == ',':
                if separate:
                    parsed.append('')
                separate = True
                i += 1
                continue
            elif data[i] == '\\':
                i += 1
                if re.match(r'\d', data[i]):
                    # This backslash is for a backreference. Insert the backslash literally.
                    if type(parsed[-1]) is str and not separate:
                        parsed[-1] += '\\'
                    elif parsed[0] != 0 and not separate:
                        if type(parsed[-1]) is list and parsed[-1][0] == 0:
                            if type(parsed[-1][-1]) is str:
                                parsed[-1][-1] += '\\'
                            else:
                                parsed[-1].append('\\')
                        else:
                            parsed[-1] = [0, parsed[-1], '\\']
                    else:
                        parsed.append('\\')
                        separate = False
                # Insert the character after the backslash literally.
                if type(parsed[-1]) is str and not separate:
                    parsed[-1] += data[i]
                elif parsed[0] != 0 and not separate:
                    if type(parsed[-1]) is list and parsed[-1][0] == 0:
                        if type(parsed[-1][-1]) is str:
                            parsed[-1][-1] += data[i]
                        else:
                            parsed[-1].append(data[i])
                    else:
                        parsed[-1] = [0, parsed[-1], data[i]]
                else:
                    parsed.append(data[i])
                    separate = False
                i += 1
                continue
            else:
                if type(parsed[-1]) is str and not separate:
                    parsed[-1] += data[i]
                elif parsed[0] != 0 and not separate:
                    if type(parsed[-1]) is list and parsed[-1][0] == 0:
                        if type(parsed[-1][-1]) is str:
                            parsed[-1][-1] += data[i]
                        else:
                            parsed[-1].append(data[i])
                    else:
                        parsed[-1] = [0, parsed[-1], data[i]]
                else:
                    parsed.append(data[i])
                    separate = False
                i += 1
        if separate:
            parsed.append('')
        return (parsed, data)
