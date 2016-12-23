import re
import random
from botbot.euphutils import EuphUtils

class Parser:
    def __init__(self, parse_string):
        temp = ''
        self.array = []
        self.parse_string = parse_string
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

    def get_messages(self, content, sender, variables):
        messages = []
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
                    variable = next(iter(self.parse_entry(parsed[0], variables)), '')
                    regex_string += re.escape(variable)
                else:
                    regex_string += raw_regex_string[i]
                    i += 1
            regex = re.compile(regex_string, re.IGNORECASE)
            match = regex.search(content)
            if match:
                messages_to_add = self.parse_entry(entry[1], variables)
                groups = match.groups('')
                i = 0
                while i < len(messages_to_add):
                    j = len(groups) - 1
                    while j >= 0:
                        messages_to_add[i] = messages_to_add[i].replace('\\' + str(j + 1), groups[j])
                        j -= 1
                    i += 1
                messages.extend(messages_to_add)
                continue
        return messages

    def get_regexes(self):
        return list(map(lambda entry: entry[0], self.array))

    def parse_entry(self, parsed_data, variables):
        result_strings = []
        i = 0
        if parsed_data[0] == 0: # concatenation
            result_strings = ['']
            for element in parsed_data[1:]:
                if type(element) is str:
                    i = 0
                    while i < len(result_strings):
                        result_strings[i] += element
                        i += 1
                else:
                    subresults = self.parse_entry(element, variables)
                    if len(subresults) == 0:
                        subresults.append('')
                    old_result_strings = result_strings
                    result_strings = []
                    for result_string in old_result_strings:
                        for subresult in subresults:
                            result_strings.append(result_string + subresult)
        elif parsed_data[0] == 1: # random choice [a,b,c]
            element = parsed_data[random.randint(1, len(parsed_data) - 1)]
            if type(element) is not str:
                result_strings = self.parse_entry(element, variables)
            else:
                result_strings = [element]
        elif parsed_data[0] == 2: # multiple response {a,b,c}
            for element in parsed_data[1:]:
                if type(element) is str:
                    result_strings.append(element)
                else:
                    result_strings += self.parse_entry(element, variables)
        elif parsed_data[0] == 3: # dynamic variable ${variable}
            variable_name = parsed_data[1]
            if type(variable_name) is not str:
                variable_name = next(iter(self.parse_entry(variable_name, variables)), '')
            result_strings = [variables.get(variable_name.strip(), '')]
        else:
            return []
        return result_strings

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
        while i < len(data):
            if separate and re.match(r'\s', data[i]):
                i += 1
                continue
            elif data[i] == endchar:
                if separate:
                    parsed.append('')
                return (parsed, data[:i + 1])
            elif data[i:].startswith(startchars):
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
