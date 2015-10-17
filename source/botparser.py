import re
import random
from euphutils import EuphUtils

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
                        self.array.append([re.compile(temp, re.IGNORECASE), [0, '']])
                    else:
                        self.array.append([re.compile(temp, re.IGNORECASE)])
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
        messages = []
        for entry in self.array:
            search_string = content
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
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
            search_string = content.replace(EuphUtils.mention(sender), '(@sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
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
            search_string = content.replace(sender, '(sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
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
            search_string = content.replace(EuphUtils.mention(sender), '(@sender)').replace(sender, '(sender)')
            match = entry[0].search(search_string)
            if match:
                messages_to_add = self.parse_entry(entry[1])
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
        regexes = []
        for entry in self.array:
            regexes.append(entry[0].pattern)
        return regexes

    def parse_entry(self, parsed_data):
        result_strings = []
        i = 0
        if parsed_data[0] == 0:
            result_strings = ['']
            for element in parsed_data[1:]:
                if type(element) is str:
                    i = 0
                    while i < len(result_strings):
                        result_strings[i] += element
                        i += 1
                else:
                    subresults = self.parse_entry(element)
                    if len(subresults) == 0:
                        subresults.append('')
                    old_result_strings = result_strings
                    result_strings = []
                    for result_string in old_result_strings:
                        for subresult in subresults:
                            result_strings.append(result_string + subresult)
        elif parsed_data[0] == 1:
            element = parsed_data[random.randint(1, len(parsed_data) - 1)]
            if type(element) is not str:
                result_strings = self.parse_entry(element)
            else:
                result_strings = [element]
        elif parsed_data[0] == 2:
            for element in parsed_data[1:]:
                if type(element) is str:
                    result_strings.append(element)
                else:
                    result_strings += self.parse_entry(element)
        else:
            return []
        return result_strings

    def parse_response_string(self, data, datatype=0):
        parsed = [datatype]
        startchars = {'[': 1, '{': 2}
        endchars = {0: ';', 1: ']', 2: '}'}
        endchar = endchars[datatype]
        i = 0
        separate = True
        while i < len(data):
            if separate and re.match(r'\s', data[i]):
                i += 1
                continue
            elif data[i] == endchar:
                if separate:
                    parsed.append('')
                return (parsed, data[:i + 1])
            elif data[i] in startchars.keys():
                subparsed = self.parse_response_string(data[i + 1:], startchars[data[i]])
                i += len(subparsed[1]) + 1
                if separate or parsed[0] == 0:
                    parsed.append(subparsed[0])
                    separate = False
                else:
                    if type(parsed[-1]) is list and parsed[-1][0] == 0:
                        parsed[-1].append(subparsed[0])
                    else:
                        parsed[-1] = [0, parsed[-1], subparsed[0]]
                continue
            elif data[i] == ',' and parsed[0] != 0:
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
