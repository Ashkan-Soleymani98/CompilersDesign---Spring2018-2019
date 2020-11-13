import p4
import sys
sys.setrecursionlimit(100000)

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


def insert_word_to_dfa(dfa, word, index):
    current_state = "q_start" if index == 0 else "q_" + word[0:index]
    next_state = "q_" + word[0:index + 1]
    if not next_state in dfa:
        dfa[next_state] = {
            "state": "reject"
        }
    dfa[current_state][word[index]] = next_state
    if index + 1 == len(word):
        dfa[next_state]["state"] = "accept"
        return
    insert_word_to_dfa(dfa, word, index + 1)


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
        chr(32): "q_accept",
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
    for i in string:
        if i not in dfa[current_state]:
            if i not in alphabet:
                return -2
            return -1
        next_state = dfa[current_state][i]
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
error_file = open("errors.txt", 'w+')

alphabet = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + ['/', ';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<'] + ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + [chr(32), chr(10), chr(13), chr(9), chr(11), chr(12), chr(0)]

input_contents = input_contents + chr(0)
found_token = ""
last_accepted_index = 0
index = 1
first_time_writing_to_error_file = True
first_time_writing_to_token_file = True
current_line = 1
token_line = 0
error_line = 0


def get_next_token():
    global index, input_contents, found_token, last_accepted_index, first_time_writing_to_token_file, first_time_writing_to_error_file, current_line, token_line, error_line, \
        dfa_keyword, dfa_id, dfa_num, dfa_symbol, dfa_comment, dfa_whitespace, dfa_eof, dfa_num, error_file
    leave = False
    while (index < len(input_contents)+1) and (not leave):
        if run_dfa(dfa_keyword, input_contents[last_accepted_index:index]) > 0:
            found_token = "KEYWORD"
            index += 1
        elif run_dfa(dfa_id, input_contents[last_accepted_index:index]) > 0:
            found_token = "ID"
            index += 1
        elif run_dfa(dfa_num, input_contents[last_accepted_index:index]) > 0:
            found_token = "NUM"
            index += 1
        elif run_dfa(dfa_symbol, input_contents[last_accepted_index:index]) > 0:
            found_token = "SYMBOL"
            index += 1
        elif run_dfa(dfa_comment, input_contents[last_accepted_index:index]) > 0:
            found_token = "COMMENT"
            index += 1
        elif run_dfa(dfa_whitespace, input_contents[last_accepted_index:index]) > 0:
            found_token = "WHITESPACE"
            index += 1
        elif run_dfa(dfa_eof, input_contents[last_accepted_index:index]) > 0:
            return ("EOF", "", 0)

        elif run_dfa(dfa_num, input_contents[last_accepted_index:index]) < -1 or run_dfa(dfa_id, input_contents[last_accepted_index:index]) < -1:
            if error_line != current_line:
                error_file.write(("\n" if not first_time_writing_to_error_file else "") + str(current_line) + ". (" + \
                                 input_contents[last_accepted_index:index] + ", " + "invalid input) ")
                error_line = current_line
                first_time_writing_to_error_file = False
            else:
                error_file.write("(" + input_contents[last_accepted_index:index] + ", " + "invalid input) ")
            last_accepted_index = index
            index += 1
        elif run_dfa(dfa_keyword, input_contents[last_accepted_index:index]) < 0 and run_dfa(dfa_id, input_contents[last_accepted_index:index]) < 0 \
            and run_dfa(dfa_symbol, input_contents[last_accepted_index:index]) < 0 and \
            run_dfa(dfa_symbol, input_contents[last_accepted_index:index]) < 0 and run_dfa(dfa_comment, input_contents[last_accepted_index:index]) < 0 and \
            run_dfa(dfa_whitespace, input_contents[last_accepted_index:index]) < 0:

            if input_contents[last_accepted_index:index-1].__contains__('\n'):
                current_line += 1
            if found_token != "WHITESPACE" and found_token != "COMMENT" and found_token != "":
                if token_line != current_line:
                    token_file.write(("\n" if not first_time_writing_to_token_file else "") + str(current_line) + ". (" + found_token + ", " + \
                                     str(input_contents[last_accepted_index:index-1]) + ") ")
                    token_line = current_line
                    first_time_writing_to_token_file = False
                    leave = True
                    tokens.append((found_token, str(input_contents[last_accepted_index:index - 1]), token_line))
                    p4.tokens_received.append((found_token, str(input_contents[last_accepted_index:index - 1]), token_line))
                else:
                    token_file.write("(" + found_token + ", " + str(input_contents[last_accepted_index:index - 1]) + ") ")
                    leave = True
                    tokens.append((found_token, str(input_contents[last_accepted_index:index-1]),token_line))
                    p4.tokens_received.append((found_token, str(input_contents[last_accepted_index:index-1]),token_line))
            last_accepted_index = index-1
            found_token = ""
        else:
            found_token = ""
            index += 1
    if leave:
        return tokens[-1]
    return None, None, None

tokens = []

# PHASE 2:
def getNextToken():
    (token, token_string, line) = get_next_token()
    if token == "KEYWORD" or token == "SYMBOL":
        token = token_string
    return token, line

diagram = {
    "program": {
        "q_start": {
            "declaration_list": "q_1",
            "state": "reject"

        },
        "q_1": {
            "EOF": "q_accept",
            "state": "reject",
            "actions": {
                "EOF":{
                    "after_parse": ["#INITIALIZER"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "declaration_list": {
        "q_start": {
            "declaration_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "declaration_list1": {
        "q_start": {
            "declaration": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "declaration_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "declaration": {
        "q_start": {
            "int": "q_1",
            "void": "q_2",
            "state": "reject"
        },
        "q_1": {
            "fint": "q_accept",
            "state": "reject"
        },
        "q_2": {
            "fvoid": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fint": {
        "q_start": {
            "ID": "q_1",
            "state": "reject"
        },
        "q_1": {
            "fid5": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fid5": {
        "q_start": {
            "fid1": "q_accept",
            "(": "q_1",
            "state": "reject",
            "actions": {
                "(":{
                    "after_parse": ["#FUNCTION_SCOPE"]
                }
            }
        },
        "q_1": {
            "params": "q_2",
            "state": "reject",
            "actions": {
                "params":{
                    "after_parse": ["#DEFINE_FUNCTION"]
                }
            }
        },
        "q_2": {
            ")": "q_3",
            "state": "reject",
        },
        "q_3": {
            "compound_stmt": "q_accept",
            "state": "reject",
            "actions": {
                "compound_stmt":{
                    "after_parse": ["#FUNCTION_FINISH", "#END_FUNCTION_SCOPE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fvoid": {
        "q_start": {
            "ID": "q_1",
            "state": "reject"
        },
        "q_1": {
            "fid6": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },

    # "actions": {
    #     "expression": {
    #         "before_parse": ["#PUSH", "#POP"],
    #         "after_parse": ["#FIND"]
    #     },
    #     "continue": {
    #         "after_parse": ["#FIND"]
    #     }
    # }

    "fid6": {
        "q_start": {
            "fid1": "q_accept",
            "(": "q_1",
            "state": "reject",
            "actions": {
                "(": {
                    "after_parse": ["#FUNCTION_SCOPE"]
                }
            }
        },
        "q_1": {
            "params": "q_2",
            "state": "reject",
            "actions": {
                "params":{
                    "after_parse": ["#DEFINE_FUNCTION"]
                }
            }
        },
        "q_2": {
            ")": "q_3",
            "state": "reject"
        },
        "q_3": {
            "compound_stmt": "q_accept",
            "state": "reject",
            "actions": {
                "compound_stmt": {
                    "after_parse": ["#FUNCTION_FINISH", "#END_FUNCTION_SCOPE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fid1":{
        "q_start": {
            ";": "q_accept",
            "[": "q_1",
            "state": "reject",
            "actions": {
                ";": {
                    "after_parse": ["#DECLARE_VARIABLE"]
                }
            }
        },
        "q_1": {
            "NUM": "q_2",
            "state": "reject",
            "actions": {
                "NUM": {
                    "after_parse": ["#DECLARE_ARRAY"]
                }
            }
        },
        "q_2": {
            "]": "q_3",
            "state": "reject"
        },
        "q_3": {
            ";": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "type_specifier": {
        "q_start": {
            "int": "q_accept",
            "void": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "params": {
        "q_start": {
            "int": "q_1",
            "void": "q_3",
            "state": "reject"
        },
        "q_1": {
            "ftype_specifier1": "q_2",
            "state": "reject"
        },
        "q_2": {
            "param_list1": "q_accept",
            "state": "reject"
        },
        "q_3": {
            "fvoid1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fvoid1": {
        "q_start": {
            "ftype_specifier1": "q_1",
            "epsilon": "q_accept",
            "state": "reject",
            "actions": {
                "epsilon": {
                    "after_parse": ["#PARAM_VOID"]
                }
            }
        },
        "q_1": {
            "param_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "param_list1": {
        "q_start": {
            ",": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "param": "q_2",
            "state": "reject"
        },
        "q_2": {
            "param_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "param": {
        "q_start": {
            "type_specifier": "q_1",
            "state": "reject"
        },
        "q_1": {
            "ftype_specifier1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "ftype_specifier1": {
        "q_start": {
            "ID": "q_1",
            "state": "reject"
        },
        "q_1": {
            "fid2": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fid2": {
        "q_start": {
            "[": "q_1",
            "epsilon": "q_accept",
            "state": "reject",
            "actions": {
                "epsilon": {
                    "after_parse": ["#PARAM_VARIABLE"]
                }
            }
        },
        "q_1": {
            "]": "q_accept",
            "state": "reject",
            "actions": {
                "]": {
                    "after_parse": ["#PARAM_ARRAY"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "compound_stmt": {
        "q_start": {
            "{": "q_1",
            "state": "reject",
            "actions": {
                "{": {
                    "after_parse": ["#NEW_SCOPE"]
                }
            }
        },
        "q_1": {
            "declaration_list": "q_2",
            "state": "reject"
        },
        "q_2": {
            "statement_list": "q_3",
            "state": "reject"
        },
        "q_3": {
            "}": "q_accept",
            "state": "reject",
            "actions": {
                "}": {
                    "after_parse": ["#EXIT_SCOPE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "statement_list": {
        "q_start": {
            "statement_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "statement_list1": {
        "q_start": {
            "statement": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "statement_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "statement": {
        "q_start": {
            "expression_stmt": "q_accept",
            "compound_stmt": "q_accept",
            "selection_stmt": "q_accept",
            "iteration_stmt": "q_accept",
            "return_stmt": "q_accept",
            "switch_stmt": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "expression_stmt": {
        "q_start": {
            "expression": "q_1",
            "continue": "q_1",
            "break": "q_1",
            ";": "q_accept",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#POP_EXPRESSION"]
                },
                "continue": {
                    "after_parse": ["#CHECK_LOOP_SCOPE"]
                },
                "break": {
                    "after_parse": ["#CHECK_BREAK_SCOPE"]
                }
            }
        },
        "q_1": {
            ";": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "selection_stmt": {
        "q_start": {
            "if": "q_1",
            "state": "reject"
        },
        "q_1": {
            "(": "q_2",
            "state": "reject"
        },
        "q_2": {
            "expression": "q_3",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#JPF_SAVE1"]
                }
            }
        },
        "q_3": {
            ")": "q_4",
            "state": "reject"
        },
        "q_4": {
            "statement": "q_5",
            "state": "reject"
        },
        "q_5": {
            "else": "q_6",
            "state": "reject",
            "actions": {
                "else": {
                    "after_parse": ["#JP_SAVE2", "#FILL_SAVE1"]
                }
            }
        },
        "q_6": {
            "statement": "q_accept",
            "state": "reject",
            "actions": {
                "statement": {
                    "after_parse": ["#FILL_SAVE2"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "iteration_stmt": {
        "q_start": {
            "while": "q_1",
            "state": "reject",
            "actions": {
                "while": {
                    "after_parse": ["#NEW_LOOP_SCOPE"]
                }
            }
        },
        "q_1": {
            "(": "q_2",
            "state": "reject",
            "actions": {
                "(": {
                    "after_parse": ["#LABEL"]
                }
            }
        },
        "q_2": {
            "expression": "q_3",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#JPF_SAVE3"]
                }
            }
        },
        "q_3": {
            ")": "q_4",
            "state": "reject"
        },
        "q_4": {
            "statement": "q_accept",
            "state": "reject",
            "actions": {
                "statement": {
                    "after_parse": ["#JP_LABEL", "#FILL_SAVE3", "#EXIT_LOOP_SCOPE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "return_stmt": {
        "q_start": {
            "return": "q_1",
            "state": "reject"
        },
        "q_1": {
            "freturn": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "freturn": {
        "q_start": {
            "expression": "q_1",
            ";": "q_accept",
            "state": "reject",
            "actions": {
                ";": {
                    "after_parse": ["#RETURN_NOTHING"]
                }
            }
        },
        "q_1": {
            ";": "q_accept",
            "state": "reject",
            "actions": {
                ";": {
                    "after_parse": ["#RETURN_FUNC"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "switch_stmt": {
        "q_start": {
            "switch": "q_1",
            "state": "reject"
        },
        "q_1": {
            "(": "q_2",
            "state": "reject"
        },
        "q_2": {
            "expression": "q_3",
            "state": "reject"
        },
        "q_3": {
            ")": "q_4",
            "state": "reject"
        },
        "q_4": {
            "{": "q_5",
            "state": "reject",
            "actions": {
                "{": {
                    "after_parse": ["#NEW_BREAK_SCOPE"]
                }
            }
        },
        "q_5": {
            "case_stmts": "q_6",
            "state": "reject"
        },
        "q_6": {
            "default_stmt": "q_7",
            "state": "reject",
            "actions": {
                "default_stmt": {
                    "after_parse": ["#EXIT_BREAK_SCOPE", "#POP_EXPRESSION"]
                }
            }
        },
        "q_7": {
            "}": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "case_stmts": {
        "q_start": {
            "case_stmts1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "case_stmts1": {
        "q_start": {
            "case_stmt": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "case_stmts1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "case_stmt": {
        "q_start": {
            "case": "q_1",
            "state": "reject"
        },
        "q_1": {
            "NUM": "q_2",
            "state": "reject",
            "actions": {
                "NUM": {
                    "after_parse": ["#PUSH_CONSTANT2", "#CMP_SAVE_CASE"]
                }
            }
        },
        "q_2": {
            ":": "q_3",
            "state": "reject"
        },
        "q_3": {
            "statement_list": "q_accept",
            "state": "reject",
            "actions": {
                "statement_list": {
                    "after_parse": ["#RUN_NEXT_CASE", "#FILL_SAVE_CASE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "default_stmt": {
        "q_start": {
            "default": "q_1",
            "epsilon": "q_accept",
            "state": "reject",
            "actions": {
                "default": {
                    "after_parse": ["#TWO_USELESS"]
                },
                "epsilon": {
                    "after_parse": ["#TWO_USELESS"]
                }
            }
        },
        "q_1": {
            ":": "q_2",
            "state": "reject"
        },
        "q_2": {
            "statement_list": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "expression": {
        "q_start": {
            "ID": "q_1_1",
            "(": "q_2_1",
            "NUM": "q_3_1",
            "+": "q_4_1",
            "-": "q_5_1",
            "state": "reject",
            "actions": {
                "NUM": {
                    "after_parse": ["#PUSH_CONSTANT"]
                }
            }
        },

        "q_1_1": {
            "fid3": "q_accept",
            "state": "reject"
        },

        "q_2_1": {
            "expression": "q_2_2",
            "state": "reject"
        },
        "q_2_2": {
            ")": "q_2_3",
            "state": "reject"
        },
        "q_2_3": {
            "term1": "q_2_4",
            "state": "reject"
        },
        "q_2_4": {
            "additive_expression1": "q_2_5",
            "state": "reject"
        },
        "q_2_5": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_3_1": {
            "term1": "q_3_2",
            "state": "reject"
        },
        "q_3_2": {
            "additive_expression1": "q_3_3",
            "state": "reject"
        },
        "q_3_3": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_4_1": {
            "factor": "q_4_2",
            "state": "reject"
        },
        "q_4_2": {
            "term1": "q_4_3",
            "state": "reject"
        },
        "q_4_3": {
            "additive_expression1": "q_4_4",
            "state": "reject"
        },
        "q_4_4": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_5_1": {
            "factor": "q_5_2",
            "state": "reject",
            "actions": {
                "factor": {
                    "after_parse": ["#NEGATIVE"]
                }
            }
        },
        "q_5_2": {
            "term1": "q_5_3",
            "state": "reject"
        },
        "q_5_3": {
            "additive_expression1": "q_5_4",
            "state": "reject"
        },
        "q_5_4": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_accept": {
            "state": "accept"
        }
    },


    "fid3": {
        "q_start": {
            "fid": "q_1_1",
            "(": "q_2_1",
            "state": "reject",
            "actions": {
                "(": {
                    "after_parse": ["#CALLEE_FUNCTION_DETECTION"]
                }
            }
        },

        "q_1_1": {
            "ffid": "q_accept",
            "state": "reject"
        },

        "q_2_1": {
            "args": "q_2_2",
            "state": "reject"
        },
        "q_2_2": {
            ")": "q_2_3",
            "state": "reject",
            "actions": {
                ")": {
                    "after_parse": ["#PUSH_RETURN_VALUE", "#GET_BACK_TO_CALLER"]
                }
            }
        },
        "q_2_3": {
            "term1": "q_2_4",
            "state": "reject"
        },
        "q_2_4": {
            "additive_expression1": "q_2_5",
            "state": "reject"
        },
        "q_2_5": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_accept": {
            "state": "accept"
        }
    },


    "ffid": {
        "q_start": {
            "=": "q_1_1",
            "*": "q_2_1",
            "addop": "q_3_1",
            "<": "q_4_1",
            "epsilon": "q_accept",
            "==": "q_4_1",
            "state": "reject",
            "actions": {
                "<": {
                    "after_parse": ["#SET_CONDITION_LESS"]
                },
                "==": {
                    "after_parse": ["#SET_CONDITION_EQUAL"]
                }
            }
        },

        "q_1_1": {
            "fmosavi": "q_accept",
            "state": "reject",
            "actions": {
                "fmosavi": {
                    "after_parse": ["#ASSIGN"]
                }
            }
        },

        "q_2_1": {
            "signed_factor": "q_2_2",
            "state": "reject",
            "actions": {
                "signed_factor": {
                    "after_parse": ["#MULT"]
                }
            }
        },
        "q_2_2": {
            "term1": "q_2_3",
            "state": "reject"
        },
        "q_2_3": {
            "additive_expression1": "q_2_4",
            "state": "reject"
        },
        "q_2_4": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_3_1": {
            "term": "q_3_2",
            "state": "reject",
            "actions": {
                "term": {
                    "after_parse": ["#ADD_SIGNED"]
                }
            }
        },
        "q_3_2": {
            "additive_expression1": "q_3_3",
            "state": "reject"
        },
        "q_3_3": {
            "fadditive_expression": "q_accept",
            "state": "reject"
        },

        "q_4_1": {
            "additive_expression": "q_accept",
            "state": "reject",
            "actions": {
                "additive_expression": {
                    "after_parse": ["#CHECK_CONDITION"]
                }
            }
        },

        "q_accept": {
            "state": "accept"
        }
    },


    "fmosavi": {
        "q_start": {
            "expression": "q_accept",
            "=": "q_1",
            "state": "reject"
        },
        "q_1": {
            "additive_expression": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fid": {
        "q_start": {
            "[": "q_1",
            "epsilon": "q_accept",
            "state": "reject",
            "actions": {
                "epsilon": {
                    "after_parse": ["#PUSH_ID"]
                },
                "[": {
                  "after_parse": ["#PUSH_ID2"]
                }
            }
        },
        "q_1": {
            "expression": "q_2",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#PUSH_ARRAY_ELEMENT"]
                }
            }
        },
        "q_2": {
            "]": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fadditive_expression": {
        "q_start": {
            "relop": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "additive_expression": "q_accept",
            "state": "reject",
            "actions": {
                "additive_expression": {
                    "after_parse": ["#CHECK_CONDITION"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "relop": {
        "q_start": {
            "==": "q_accept",
            "<": "q_accept",
            "state": "reject",
            "actions": {
                "==": {
                    "after_parse": ["#SET_CONDITION_EQUAL"]
                },
                "<": {
                    "after_parse": ["#SET_CONDITION_LESS"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "additive_expression": {
        "q_start": {
            "term": "q_1",
            "state": "reject"
        },
        "q_1": {
            "additive_expression1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "additive_expression1": {
        "q_start": {
            "addop": "q_1",
            "epsilon": "q_accept",
            "state": "reject"
        },
        "q_1": {
            "term": "q_2",
            "state": "reject",
            "actions": {
                "term": {
                    "after_parse": ["#ADD_SIGNED"]
                }
            }
        },
        "q_2": {
            "additive_expression1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "addop": {
        "q_start": {
            "+": "q_accept",
            "-": "q_accept",
            "state": "reject",
            "actions": {
                "+": {
                    "after_parse": ["#SET_SIGN_POSITIVE"]
                },
                "-": {
                   "after_parse": ["#SET_SIGN_NEGATIVE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "term": {
        "q_start": {
            "signed_factor": "q_1",
            "state": "reject"
        },
        "q_1": {
            "term1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "term1": {
        "q_start": {
            "epsilon": "q_accept",
            "*": "q_1",
            "state": "reject"
        },
        "q_1": {
            "signed_factor": "q_2",
            "state": "reject",
            "actions": {
                "signed_factor": {
                    "after_parse": ["#MULT"]
                }
            }
        },
        "q_2": {
            "term1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "signed_factor": {
        "q_start": {
            "factor": "q_accept",
            "+": "q_1",
            "-": "q_2",
            "state": "reject"
        },
        "q_1": {
            "factor": "q_accept",
            "state": "reject"
        },
        "q_2": {
            "factor": "q_accept",
            "state": "reject",
            "actions": {
                "factor": {
                    "after_parse": ["#NEGATIVE"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "factor": {
        "q_start": {
            "NUM": "q_accept",
            "(": "q_1_1",
            "ID": "q_2_1",
            "state": "reject",
            "actions": {
                "NUM": {
                    "after_parse": ["#PUSH_CONSTANT"]
                }
            }
        },
        "q_1_1": {
            "expression": "q_1_2",
            "state": "reject"
        },
        "q_1_2": {
            ")": "q_accept",
            "state": "reject"
        },
        "q_2_1": {
            "fid4": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "fid4": {
        "q_start": {
            "fid": "q_accept",
            "(": "q_1",
            "state": "reject",
            "actions": {
                "(": {
                    "after_parse": ["#CALLEE_FUNCTION_DETECTION"]
                }
            }
        },
        "q_1": {
            "args": "q_2",
            "state": "reject"
        },
        "q_2": {
            ")": "q_accept",
            "state": "reject",
            "actions": {
                ")": {
                    "after_parse": ["#PUSH_RETURN_VALUE", "#GET_BACK_TO_CALLER"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "args": {
        "q_start": {
            "epsilon": "q_accept",
            "arg_list": "q_accept",
            "state": "reject",
            "actions": {
                "epsilon": {
                    "after_parse": ["#CHECK_NUMBER_OF_ARGUMENTS", "#CALL"]
                }
            }
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "arg_list": {
        "q_start": {
            "expression": "q_1",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#ADD_ARGUMENT"]
                }
            }
        },
        "q_1": {
            "arg_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    },


    "arg_list1": {
        "q_start": {
            "epsilon": "q_accept",
            ",": "q_1",
            "state": "reject",
            "actions": {
                "epsilon": {
                    "after_parse": ["#CHECK_NUMBER_OF_ARGUMENTS", "#CALL"]
                }
            }
        },
        "q_1": {
            "expression": "q_2",
            "state": "reject",
            "actions": {
                "expression": {
                    "after_parse": ["#ADD_ARGUMENT"]
                }
            }
        },
        "q_2": {
            "arg_list1": "q_accept",
            "state": "reject"
        },
        "q_accept": {
            "state": "accept"
        }
    }
}

terminal = ['==', 'EOF', 'ID', 'NUM', 'int', 'void', '(', ')', '{', '}', '[', ']', ';', ',', 'case', 'default', 'switch', 'return', 'continue', 'break', 'while', ':', '+', '-', '=', '<', '*', 'if', 'else']


first = {
    "program": ['EOF', 'int', 'void'],
    "declaration_list1": ['int', 'void', 'epsilon'],
    "declaration": ['int', 'void'],
    "fint": ['ID'],
    "fid5": ['(', ';', '['],
    "fvoid": ['ID'],
    "fid6": ['(', ';', '['],
    "fid1": [';', '['],
    'params': ['int', 'void'],
    "fvoid1": ['ID', 'epsilon'],
    "param_list1": [',', 'epsilon'],
    "param": ['int', 'void'],
    "type_specifier": ['int', 'void'],
    "ftype_specifier1": ['ID'],
    "fid2": ['[', 'epsilon'],
    "declaration_list": ['int', 'void', 'epsilon'],
    "statement_list1": ['continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(', 'NUM', '+', '-', 'epsilon'],
    "compound_stmt": ['{'],
    "expression_stmt": ['continue', 'break', ';', 'ID', '(', 'NUM', '+', '-'],
    "selection_stmt": ['if'],
    "iteration_stmt": ['while'],
    "statement": ['continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(', 'NUM', '+', '-'],
    "return_stmt": ['return'],
    "freturn": [';', 'ID', '(', 'NUM', '+', '-'],
    "switch_stmt": ['switch'],
    "case_stmts": ['case', 'epsilon'],
    "case_stmts1": ['case', 'epsilon'],
    "case_stmt": ['case'],
    "default_stmt": ['default', 'epsilon'],
    "statement_list": ['continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(', 'NUM', '+', '-', 'epsilon'],
    "fid3": ['(', '[', '=', '*', '<', '+', '-', 'epsilon', '=='],
    "ffid": ['=', '*', '<', '+', '-', 'epsilon', '=='],
    "fmosavi": ['ID', '(', 'NUM', '+', '-'],
    "fadditive_expression": ['<', 'epsilon', '=='],
    "relop": ['<', '=='],
    "additive_expression": ['+', '-', '(', 'ID', 'NUM'],
    "additive_expression1": ['+', '-', 'epsilon'],
    "addop": ['+', '-'],
    "term": ['+', '-', '(', 'ID', 'NUM'],
    "term1": ['*', 'epsilon'],
    "signed_factor": ['+', '-', '(', 'ID', 'NUM'],
    "factor": ['(', 'ID', 'NUM'],
    "fid4": ['(', '[', 'epsilon'],
    "fid": ['[', 'epsilon'],
    "args": ['ID', '(', 'NUM', '+', '-', 'epsilon'],
    "arg_list": ['ID', '(', 'NUM', '+', '-'],
    "expression": ['ID', '(', 'NUM', '+', '-'],
    "arg_list1": [',', 'epsilon']
}

follow = {
    "program": ['$'],
    "declaration_list1": ['EOF',  'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(', 'NUM',
                          '+', '-', '}'],
    "declaration": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "fint": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "fid5": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "fvoid": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "fid6": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "fid1": ['int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    'params': [')'],
    "fvoid1": [')'],
    "param_list1": [')'],
    "param": [')', ','],
    "type_specifier": ['ID'],
    "ftype_specifier1": [',', ')'],
    "fid2": [',', ')'],
    "declaration_list": ['EOF',  'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(', 'NUM',
                            '+', '-', '}'],
    "statement_list1": ['case', 'default', '}'],
    "compound_stmt": ['case', 'default', 'else', 'int', 'void', 'EOF', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "expression_stmt": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "selection_stmt": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "iteration_stmt": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "statement": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "return_stmt": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "freturn": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "switch_stmt": ['case', 'default', 'else', 'continue', 'break', ';', '{', 'if', 'while', 'return', 'switch', 'ID', '(',
                    'NUM', '+', '-', '}'],
    "case_stmts": ['default', '}'],
    "case_stmts1": ['default', '}'],
    "case_stmt": ['case', 'default', '}'],
    "default_stmt": ['}'],
    "statement_list": ['case', 'default', '}'],
    "fid3": [';', ']', ')', ','],
    "ffid": [';', ']', ')', ','],
    "fmosavi": [';', ']', ')', ','],
    "fadditive_expression": [';', ']', ')', ','],
    "relop": ['+', '-', '(', 'ID', 'NUM'],
    "additive_expression": [';', ']', ')', ','],
    "additive_expression1": ['<', ';', ']', ')', ',', '=='],
    "addop": ['+', '-', '(', 'ID', 'NUM'],
    "term": ['+', '-', '<', ';', ']', ')', ',', '=='],
    "term1": ['+', '-', '<', ';', ']', ')', ',', '=='],
    "signed_factor": ['*', '+', '-', '<', ';', ']', ')', ',', '=='],
    "factor": ['*', '+', '-', '<', ';', ']', ')', ',', '=='],
    "fid4": ['*', '+', '-', '<', ';', ']', ')', ',', '=='],
    "fid": ['*', '+', '-', '<', '=', ';', ']', ')', ',', '=='],
    "args": [')'],
    "arg_list": [')'],
    "expression": [';', ']', ')', ','],
    "arg_list1": [')']
}
tree_file = open("parse_tree.txt", "w+")


def print_node(node):
    global tree_file
    tree_file.write("\t" * node.depth + str(node.name) + "\n")


def is_terminal(edge):
    global terminal
    return True if edge in terminal else False


def is_epsilon(edge):
    return (edge == "epsilon")


def print_error(mesg):
    global error_line, error_file, first_time_writing_to_error_file, current_line
    if error_line != current_line:
        error_file.write(("\n" if not first_time_writing_to_error_file else "") + str(current_line) + ". " + mesg + " \t")
        error_line = current_line
        first_time_writing_to_error_file = False
    else:
        error_file.write(mesg + " ")


class transition:
    def __init__(self, diagram, depth, current_state, parent, name):
        self.depth = depth
        self.current_state = current_state
        self.diagram = diagram
        self.parent = parent
        self.children = list()
        self.name = name

    def run_diagram(self, next_token, line):
        global error_line, current_line, error_file, first_time_writing_to_error_file
        print(self.name)
        if is_terminal(self.name):
            if next_token == self.name:
                next_token, line = getNextToken()
                return next_token, line
        elif is_epsilon(self.name):
            return next_token, line
        error, edge = self.find_edge(next_token)
        self.run_action_before_parse(edge)
        while self.current_state != "q_accept":
            if error == 0:
                print_error(str(line) + ": Syntax Error! Missing Non-Terminal " + str(edge))
                transition_diagram = transition(diagram[edge], self.depth + 1, "q_start", self, edge)
                self.children.append(transition_diagram)
                print_node(transition_diagram)
                self.current_state = self.diagram[self.current_state][edge]
                error, edge = self.find_edge(next_token)

                # return next_token, line
            elif error == -1:
                if next_token == "EOF":
                    print_error(str(line) + ": Syntax Error! Unexpected EndOfFile!")
                    sys.exit()
                print_error(str(line) + ": Syntax Error! Unexpected Terminal " + str(next_token))
                next_token, line = getNextToken()
                error, edge = self.find_edge(next_token)
            elif error == -2:
                if edge == "EOF":
                    print_error(str(line) + ": Syntax Error! Malformed Input!")
                    sys.exit()
                print_error(str(line) + ": Syntax Error! Missing Terminal " + str(edge))

                # It was not explained clearly if we should insert the missing terminal into the parse tree or not? Assumed YES.
                transition_diagram = transition(None, self.depth + 1, "q_accept", self, edge)
                self.children.append(transition_diagram)
                print_node(transition_diagram)
                self.current_state = self.diagram[self.current_state][edge]
                error, edge = self.find_edge(next_token)
                #return next_token, line
            else:
                if is_terminal(edge) or is_epsilon(edge):
                    transition_diagram = transition(None, self.depth + 1, "q_accept", self, edge)
                else:
                    transition_diagram = transition(diagram[edge], self.depth + 1, "q_start", self, edge)
                self.children.append(transition_diagram)
                print_node(transition_diagram)
                next_token, line = transition_diagram.run_diagram(next_token, line)
                self.run_action_after_parse(edge)
                print("Back to : " + str(self.name))
                self.current_state = self.diagram[self.current_state][edge]
                error, edge = self.find_edge(next_token)
        return next_token, line

    def find_edge(self, token):
        type_error = -1
        return_edge = None
        for edge in self.diagram[self.current_state]:
            if edge == "state" or edge == "actions":
                continue
            if is_epsilon(edge) and token in follow[self.name]:
                return 1, edge
            elif is_epsilon(edge):
                continue
            if self.check_first(token, edge) or (self.check_first("epsilon", edge) and self.check_follow(token, edge)):
                return 1, edge
            elif self.check_follow(token, edge):
                type_error = 0
                return_edge = edge
            if is_terminal(edge):
                type_error = -2
                return_edge = edge
        return type_error, return_edge

    def check_follow(self, token, edge):
        if is_terminal(edge):
            return False
        if token in follow[edge]:
            return True
        return False

    def check_first(self, token, edge):
        if is_terminal(edge):
            return token == edge
        try:
            if token in first[edge]:
                return True
        except KeyError:
            print("$$$$$$$$$$$$" + edge)
        return False

    def run_action_before_parse(self, edge):
        if "actions" in self.diagram[self.current_state]:
            if edge in self.diagram[self.current_state]["actions"]:
                if "before_parse" in self.diagram[self.current_state]["actions"][edge]:
                    for routine in self.diagram[self.current_state]["actions"][edge]["before_parse"]:
                        print("semantic routine " + routine)
                        p4.semantic_routine(routine)

    def run_action_after_parse(self, edge):
        if "actions" in self.diagram[self.current_state]:
            if edge in self.diagram[self.current_state]["actions"]:
                if "after_parse" in self.diagram[self.current_state]["actions"][edge]:
                    for routine in self.diagram[self.current_state]["actions"][edge]["after_parse"]:
                        print("semantic routine " + routine)
                        p4.semantic_routine(routine)


transition_obj = transition(diagram["program"], 0, "q_start", None, "program")
token, line = getNextToken()
print_node(transition_obj)
transition_obj.run_diagram(token, line)

print(len(p4.PB))
for k in range(len(p4.PB)):
    print(str(k) + "\t" + p4.PB[k])