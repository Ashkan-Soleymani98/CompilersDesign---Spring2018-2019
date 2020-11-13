dfa_num = {
    "q_start": {
        "0": "q_accept",
        "1": "q_accept",
        "2": "q_accept",
        "3": "q_accept",
        "4": "q_accept",
        "5": "q_accept",
        "6": "q_accept",
        "7": "q_accept",
        "8": "q_accept",
        "9": "q_accept",
        "state": "reject"
    },
    "q_accept": {
        "0": "q_accept",
        "1": "q_accept",
        "2": "q_accept",
        "3": "q_accept",
        "4": "q_accept",
        "5": "q_accept",
        "6": "q_accept",
        "7": "q_accept",
        "8": "q_accept",
        "9": "q_accept",
        "state": "accept"
    }
}

dfa_id = {
    "q_start": {
        "state": "reject"
    },
    "q_accept": {
        "0": "q_accept",
        "1": "q_accept",
        "2": "q_accept",
        "3": "q_accept",
        "4": "q_accept",
        "5": "q_accept",
        "6": "q_accept",
        "7": "q_accept",
        "8": "q_accept",
        "9": "q_accept",
        "state": "accept"
    }
}

for i in range(ord("a"), ord("z") + 1):
    dfa_id["q_start"][chr(i)] = "q_accept"
    dfa_id["q_accept"][chr(i)] = "q_accept"

for i in range(ord("A"), ord("Z") + 1):
    dfa_id["q_start"][chr(i)] = "q_accept"
    dfa_id["q_accept"][chr(i)] = "q_accept"


def insert_word_to_dfa(dfa, input_word, index):
    current_state = "q_start" if index == 0 else "q_" + input_word[0:index]
    next_state = "q_" + input_word[0:index + 1]
    if next_state not in dfa:
        dfa[next_state] = {
            "state": "reject"
        }
    dfa[current_state][input_word[index]] = next_state
    if index + 1 == len(input_word):
        dfa[next_state]["state"] = "accept"
        return
    insert_word_to_dfa(dfa, input_word, index + 1)


dfa_keyword = {
    "q_start": {

    }
}

keywords = ["break", "case", "continue", "default", "else", "if", "int", "return", "switch", "void", "while"]
for word in keywords:
    insert_word_to_dfa(dfa_keyword, word, 0)

dfa_symbol = {
    "q_start": {
        ";": "q_accept_1",
        ":": "q_accept_1",
        ",": "q_accept_1",
        "[": "q_accept_1",
        "]": "q_accept_1",
        "(": "q_accept_1",
        ")": "q_accept_1",
        "{": "q_accept_1",
        "}": "q_accept_1",
        "+": "q_accept_1",
        "-": "q_accept_1",
        "*": "q_accept_1",
        "=": "q_accept_2",
        "<": "q_accept_1",
        "state": "reject"
    },
    "q_accept_1": {
        "state": "accept"
    },
    "q_accept_2": {
        "state": "accept",
        "=": "q_accept_3"
    },
    "q_accept_3": {
        "state": "accept"
    }
}

comment_content_method1 = list(range(0, 128))
comment_content_method1.remove(ord("*"))
comment_content_method2 = list(range(0, 128))
comment_content_method2.remove(ord("/"))
comment_content_method3 = list(range(0, 128))
comment_content_method3.remove(ord("\n"))
dfa_comment = {
    "q_start": {
        "/": "q_/",
        "state": "reject"
    },
    "q_/": {
        "*": "q_/*",
        "/": "q_//",
        "state": "reject"
    },
    "q_/*": {
        "*": "q_/**",
        "state": "reject"
    },
    "q_/**": {
        "/": "q_accept",
        "state": "reject"
    },
    "q_//": {
        "\n": "q_accept",
        "state": "reject"
    },
    "q_accept": {
        "state": "accept"
    }
}

for char in comment_content_method1:
    dfa_comment["q_/*"][chr(char)] = "q_/*"

for char in comment_content_method2:
    dfa_comment["q_/**"][chr(char)] = "q_/*"

for char in comment_content_method3:
    dfa_comment["q_//"][chr(char)] = "q_//"


dfa_whitespace = {
    "q_start": {
        "state": "reject",
        " ": "q_accept",
        chr(32): "q_accept",  # blank
        "\n": "q_accept",
        "\r": "q_accept",
        "\t": "q_accept",
        "\v": "q_accept",
        "\f": "q_accept"
    },
    "q_accept": {
        "state": "accept"
    }
}

dfa_eof = {
    "q_start": {
        "state": "reject",
        chr(0): "q_accept"
    },
    "q_accept": {
        "state": "accept"
    }
}


def run_dfa(dfa, string):
    current_state = "q_start"
    for x in string:
        if x not in dfa[current_state]:
            if x not in alphabet:
                return -2
            return -1
        next_state = dfa[current_state][x]
        current_state = next_state
    if dfa[current_state]["state"] == "accept":
        return 1
    else:
        return 0


input_file = open("input.txt", "r")
if input_file.mode == 'r':
    input_contents = input_file.read()
input_file.close()

token_file = open("scanner.txt", 'w+')
error_file = open("lexical_errors.txt", 'w+')

alphabet = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + \
           ['/', ';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<'] + \
           ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + [chr(32), chr(10), chr(13), chr(9), chr(11), chr(12), chr(0)]

# PHASE 2:
token_pointer = 0
tokens = []


def getNextToken():
    global token_pointer, tokens
    while token_pointer >= len(tokens):
        pass
    token_pointer += 1
    token, line = tokens[token_pointer - 1]
    return token, line


input_contents = input_contents + chr(0)
found_token = ""
last_accepted_index = 0
i = 1
first_time_writing_to_error_file = True
first_time_writing_to_token_file = True
current_line = 1
token_line = 0
error_line = 0


def get_next_token():
    global i, input_contents, found_token, last_accepted_index, first_time_writing_to_token_file, first_time_writing_to_error_file, current_line, token_line, error_line, \
        dfa_keyword, dfa_id, dfa_num, dfa_symbol, dfa_comment, dfa_whitespace, dfa_eof, dfa_num, error_file
    leave = False
    while i < len(input_contents)+1 and (not leave):
        if run_dfa(dfa_keyword, input_contents[last_accepted_index:i]) > 0:
            found_token = "KEYWORD"
            i += 1
        elif run_dfa(dfa_id, input_contents[last_accepted_index:i]) > 0:
            found_token = "ID"
            i += 1
        elif run_dfa(dfa_num, input_contents[last_accepted_index:i]) > 0:
            found_token = "NUM"
            i += 1
        elif run_dfa(dfa_symbol, input_contents[last_accepted_index:i]) > 0:
            found_token = "SYMBOL"
            i += 1
        elif run_dfa(dfa_comment, input_contents[last_accepted_index:i]) > 0:
            found_token = "COMMENT"
            i += 1
        elif run_dfa(dfa_whitespace, input_contents[last_accepted_index:i]) > 0:
            found_token = "WHITESPACE"
            i += 1
        elif run_dfa(dfa_eof, input_contents[last_accepted_index:i]) > 0:
            return ("EOF", "", 0)

        elif run_dfa(dfa_num, input_contents[last_accepted_index:i]) < -1 or run_dfa(dfa_id, input_contents[last_accepted_index:i]) < -1:
            if error_line != current_line:
                error_file.write(("\n" if not first_time_writing_to_error_file else "") + str(current_line) + ". (" + \
                                 input_contents[last_accepted_index:i] + ", " + "invalid input) ")
                error_line = current_line
                first_time_writing_to_error_file = False
            else:
                error_file.write("(" + input_contents[last_accepted_index:i] + ", " + "invalid input) ")
            last_accepted_index = i
            i += 1
        elif run_dfa(dfa_keyword, input_contents[last_accepted_index:i]) < 0 and run_dfa(dfa_id, input_contents[last_accepted_index:i]) < 0 \
            and run_dfa(dfa_symbol, input_contents[last_accepted_index:i]) < 0 and \
            run_dfa(dfa_symbol, input_contents[last_accepted_index:i]) < 0 and run_dfa(dfa_comment, input_contents[last_accepted_index:i]) < 0 and \
            run_dfa(dfa_whitespace, input_contents[last_accepted_index:i]) < 0:
            if found_token == "":
                if error_line != current_line:
                    error_file.write(
                        ("\n" if not first_time_writing_to_error_file else "") + str(current_line) + ". (" + \
                        input_contents[last_accepted_index:i] + ", " + "invalid input) ")
                    error_line = current_line
                    first_time_writing_to_error_file = False
                else:
                    error_file.write("(" + input_contents[last_accepted_index:i] + ", " + "invalid input) ")

            if input_contents[last_accepted_index:i-1].__contains__('\n'):
                current_line += 1
            if found_token != "WHITESPACE" and found_token != "COMMENT" and found_token != "":
                if token_line != current_line:
                    token_file.write(("\n" if not first_time_writing_to_token_file else "") + str(current_line) + ". (" + found_token + ", " + \
                                     str(input_contents[last_accepted_index:i-1]) + ") ")
                    token_line = current_line
                    first_time_writing_to_token_file = False
                else:
                    token_file.write("(" + found_token + ", " + str(input_contents[last_accepted_index:i-1]) + ") ")
                leave = True
                tokens.append((found_token, token_line))
            last_accepted_index = i-1
            found_token = ""

        else:
            found_token = ""
            i += 1
    if leave:
        return tokens[-1]
    return None

while get_next_token() != ("EOF", "", 0):
    pass

token_file.close()
error_file.close()