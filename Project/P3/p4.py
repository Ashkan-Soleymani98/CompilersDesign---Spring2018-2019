# import P3
import sys

int_size = 4

PB = ["" for index in range(100)]
index = 1
tokens_received = []


initial_temp_pointer = 1000
temp_pointer = initial_temp_pointer
temp_pointer_step = 4


def get_temp_addr():
    global temp_pointer
    temp_pointer += temp_pointer_step
    return temp_pointer - temp_pointer_step


def translate_two_indirect_address(address1, address2, address3):
    global PB, index
    t1 = address1 = str(address1)
    t2 = address2 = str(address2)
    t3 = address3 = str(address3)
    if "@@" in address1:
        t1 = get_temp_addr()
        PB[index] = "(ASSIGN, @{}, {}, )".format(address1[2:], t1)
        index = index + 1
        t1 = "@" + str(t1)
    if "@@" in address2:
        t2 = get_temp_addr()
        PB[index] = "(ASSIGN, @{}, {}, )".format(address2[2:], t2)
        index = index + 1
        t2 = "@" + str(t2)
    if "@@" in address3:
        t3 = get_temp_addr()
        PB[index] = "(ASSIGN, @{}, {}, )".format(address3[2:], t3)
        index = index + 1
        t3 = "@" + str(t3)
    if "#@" in address1:
        t1 = address1[2:]
    if "#@" in address2:
        t2 = address3[2:]
    if "#@" in address3:
        t3 = address3[2:]
    return t1, t2, t3


initial_stack_pointer = 2000
stack_pointer = initial_stack_pointer
stack_pointer_step = 50


def get_stack_addr():
    global stack_pointer
    stack_pointer += stack_pointer_step
    return stack_pointer - stack_pointer_step


initial_activation_pointer = 10000
activation_pointer = initial_activation_pointer
activation_pointer_step = 300


def get_activation_addr():
    global activation_pointer
    activation_pointer += activation_pointer_step
    return activation_pointer - activation_pointer_step


# create static activation when declare, create dynamic activation when caller calls, and
# run dynamic_finder function in callee and return_func when return
class static_activation:
    global index

    '''
    static activation record: (parts, size)
        ...


    '''
    def __init__(self, name, num_of_parameters, type_of_parameters, parent_static_address, output_type):
        global index
        self.name = name
        self.num_of_parameters = num_of_parameters
        self.type_of_parameters = type_of_parameters
        self.access_link = parent_static_address
        self.recurrent_counter_address = get_temp_addr()  # must be initialized to 0(PB[i] = ...)
        # PB[index] = "(ASSIGN, #0, %d, )".format(self.recurrent_counter_address)
        # index += 1 ُ## TODO
        self.stack_pointer = get_stack_addr()
        self.start_line = index #TODO
        self.output_type = output_type
        self.symbol_table = {

        }
        self.pseudo_counter = 0

    def dynamic_finder(self):  # return respective dynamic activation record
        global index
        t = get_temp_addr()  # address of respective dynamic record
        PB[index] = "(ADD, #{}, {}, {})".format(self.stack_pointer,
                                               self.recurrent_counter_address,
                                               t)
        index += 1
        # PB[index] = "(ASSIGN, @%d, %d, )".format(t, t)
        # index += 1
        ghost_dynamic_record = dynamic_activation(static_record=display[self.name], ghost=True, pointer_ghost=t)
        return ghost_dynamic_record


class dynamic_activation:
    global index

    '''
    dynamic activation record: (parts, size)
        1. return value, 4
        2. actual parameters, 4 * num
        3. control link, 4
        4. return address, 4
        5. local data pointer, 4
        6. local data

    '''
    def __init__(self, static_record, parameters=None, control_link=None, return_address=None, ghost=False, pointer_ghost=None):
        global PB, index
        self.static_record = static_record
        if ghost:
            # it keeps all of attributes as addresses
            t = get_temp_addr()
            PB[index] = "(ASSIGN, @{}, {}, )".format(pointer_ghost, t)
            index += 1
            self.return_value_address = "@" + str(t)
            self.parameters_address = []
            for w in range(4, 4 * (self.static_record.num_of_parameters + 1), 4):
                t = get_temp_addr()
                PB[index] = "(ADD, @{}, #{}, {})".format(pointer_ghost, w, t)
                self.parameters_address.append("@" + str(t))
                index += 1
            j = 4 * (self.static_record.num_of_parameters + 1)
            #
            # self.parameters_address = [("@" + str((self.return_value_address + j))) for j in
            #                            range(0, 4 * self.static_record.num_of_parameters, 4)]
            t = get_temp_addr()
            # PB[index] = "(ADD, {}, #{}, {})".format(pointer_ghost, j, t) ### control link intermediate code
            self.control_link_address = "@" + str(t)
            j += 4
            # self.control_link_address = "@" + str(pointer_ghost + 4 * self.static_record.num_of_parameters)
            t = get_temp_addr()
            PB[index] = "(ADD, @{}, #{}, {})".format(pointer_ghost, j, t)
            index += 1
            self.return_address_address = "@" + str(t)
            j += 4
            # self.return_address_address = "@" + str(self.control_link_address + 4)
            t = get_temp_addr()
            PB[index] = "(ADD, @{}, #{}, {})".format(pointer_ghost, j, t)
            index += 1
            self.local_data_pointer_address = "@" + str(t)
            # j += 4
            # self.local_data_pointer_address = "@" + str(self.return_address_address + 4)
            for j, symbol in enumerate(self.static_record.symbol_table):
                t = self.static_record.symbol_table[symbol]
                a, b, c = translate_two_indirect_address("#" + str(self.local_data_pointer_address),
                                                         "#" + str(j * 4), t)
                self.static_record.symbol_table[symbol] = c
                PB[index] = "(ADD, {}, {}, {})".format(a, b, c)
                print("in find" + PB[index])
                index += 1
        else:
            self.static_record = static_record
            self.parameters = parameters
            self.control_link = control_link
            self.return_address = return_address
            self.address = get_activation_addr()
            self.set_static_record()
            self.set_dynamic_record()

    def set_static_record(self):
        global index, PB
        # set static stack pointer and recurrent counter
        t = get_temp_addr()
        PB[index] = "(ADD, {}, #4, {})".format(self.static_record.recurrent_counter_address,
                                               self.static_record.recurrent_counter_address)
        index += 1

        PB[index] = "(ADD, #{}, {}, {})".format(self.static_record.stack_pointer,
                                               self.static_record.recurrent_counter_address,
                                               t)
        index += 1

        PB[index] = "(ASSIGN, #{}, @{}, )".format(self.address, t)
        index += 1

    def set_dynamic_record(self):
        global index, PB
        self.return_value_address = self.address
        self.parameters_address = [(self.return_value_address + j + 4) for j in
                                   range(0, 4 * self.static_record.num_of_parameters, 4)]
        self.control_link_address = self.address + 4 * self.static_record.num_of_parameters + 4
        self.return_address_address = self.control_link_address + 4
        self.local_data_pointer_address = self.return_address_address + 4

        for parameter_address, parameter in zip(self.parameters_address, self.parameters):
            PB[index] = "(ASSIGN, {}, {}, )".format(parameter, parameter_address)
            index += 1
        # PB[index] = "(ASSIGN, #{}, {}, )".format(self.control_link, self.control_link_address)
        # index += 1
        PB[index] = "(ASSIGN, #{}, {}, )".format(self.return_address, self.return_address_address)
        index += 1
        # PB[index] = "(ASSIGN, #4, {}, )".format(self.local_data_pointer_address)
        # index += 1

    def return_func(self, return_value):
        global index, PB
        PB[index] = "(ASSIGN, {}, {}, )".format(return_value, self.return_value_address)
        index += 1
        PB[index] = "(SUB, {}, #4, {})".format(self.static_record.recurrent_counter_address,
                                               self.static_record.recurrent_counter_address)
        index += 1
        a, b, c = translate_two_indirect_address("@" + str(self.return_address_address), "", "")
        PB[index] = "(JP, {}, , )".format(a)
        index += 1
        return self.return_value_address

    def get_dynamic_temp_addr(self, symbol):
        global index, PB
        if symbol not in self.static_record.symbol_table:
            t = get_temp_addr()
            a, b, c = translate_two_indirect_address("#" + str(self.local_data_pointer_address),
                                                     "#" + str(len(self.static_record.symbol_table) * 4), t)
            self.static_record.symbol_table[symbol] = c
            PB[index] = "(ADD, {}, {}, {})".format(a, b, c)
            print("in get_address " + PB[index])
            index += 1
            return "@" + str(c)
        else:
            return "@" + self.static_record.symbol_table[symbol]

    def get_pseudo_dynamic_temp_addr(self):
        self.static_record.pseudo_counter += 1
        return self.get_dynamic_temp_addr(str(self.static_record.pseudo_counter))


display = {
    "global": static_activation("global", 0, [], None, ""),
}



# OUTPUT DEFINITION ################################################################
display["output"] = static_activation("output", 1, ["int"], display["global"], "void")
last_dynamic = display["output"].dynamic_finder()
param_address = last_dynamic.parameters_address

PB[index] = "(PRINT, {}, , )".format(param_address[0])
index += 1

last_return_type = "void"
last_return_value = 0
last_return_value_address = last_dynamic.return_func(0)
##########################################################################################

scope_vars = [("global", None, None, None)]
pb_of_breaks = []
saved_pbs = []
ss = []
type_stack = []
labels = []
constants = []
count_params = 0
type_of_params = []
name_of_params = []
last_sign = "positive"
last_condition = "less"
function_output_type = "void"
last_dynamic = 0
last_return_value_address = 0
callee_static = []
callee_name = []
arguments = []
count_arguments = 0
level_of_break = 0
saved_arrays_declaration_pbs = []


def add_scope(name, type, start_i):
    global scope_vars
    scope_vars.append((name, type, start_i, None))


def add_variable(name, type, address, num=1):
    global scope_vars
    scope_vars.append((name, type, address, num))


def is_dynamic():
    global scope_vars
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "function" and name != "main" and n is None:
            return True
    return False


def declare_variable():
    global last_dynamic
    _, x1, _ = tokens_received[-4]
    _, x2, _ = tokens_received[-3]
    # print(tokens_received[-1], tokens_received[-2], tokens_received[-3], tokens_received[-4])
    if x1 == "void":
        print("ERROR")
    if not is_dynamic():
        add_variable(x2, x1, get_temp_addr())
    else:
        address = last_dynamic.get_dynamic_temp_addr(x2)
        add_variable(x2, x1, address)


def declare_array():
    global index, PB, last_dynamic, saved_arrays_declaration_pbs
    _, x1, _ = tokens_received[-4]
    _, x2, _ = tokens_received[-5]
    _, x3, _ = tokens_received[-2]
    # print(tokens_received[-1], tokens_received[-2], tokens_received[-3], tokens_received[-4], tokens_received[-5])
    if x2 == "void":
        print("ERROR")
    if not is_dynamic():
        t = get_temp_addr()
        for j in range(int(x3) - 1):
            get_temp_addr()
        pointer = get_temp_addr()
        # PB[index] = "(ASSIGN, #{}, {}, , )".format(t, pointer)
        # index += 1
        saved_arrays_declaration_pbs.append("(ASSIGN, #{}, {}, )".format(t, pointer))
        add_variable(name=x1, type=x2, address=pointer, num=int(x3))
    else:
        t = last_dynamic.get_dynamic_temp_addr(str(x1) + str(0))
        for j in range(1, int(x3)):
            last_dynamic.get_dynamic_temp_addr(str(x1) + str(j))
        pointer = last_dynamic.get_dynamic_temp_addr(str(x1))
        a, b, c = translate_two_indirect_address("#" + str(t), pointer, "")
        PB[index] = "(ASSIGN, {}, {}, )".format(a, b)
        index += 1
        add_variable(x1, x2, pointer, int(x3))


def function_scope():
    global index, function_output_type
    _, x1, _ = tokens_received[-3]
    add_scope(x1, "function", index)
    _, x2, _ = tokens_received[-4]
    function_output_type = x2


def end_function_scope():
    global scope_vars
    print(scope_vars)
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "function" and n is None:
            print(scope_vars)
            del scope_vars[j]
            #scope_vars.remove(scope_vars[j])
            print(scope_vars)
            return
        else:
            del scope_vars[j]
            #scope_vars.remove(scope_vars[j])


def param_void():
    global index, count_params
    type_of_params.append("void")
    count_params = 0


def param_variable():
    global index, scope_vars, count_params
    _, x1, _ = tokens_received[-3]
    _, x2, _ = tokens_received[-2]
    type_of_params.append(x1)
    name_of_params.append(x2)
    if x1 == "void":
        print("Illegal type of void.")
        sys.exit()
    count_params += 1


def param_array():
    global count_params
    _, x1, _ = tokens_received[-5]
    _, x2, _ = tokens_received[-4]
    type_of_params.append(x1 + " []")
    name_of_params.append(x2)
    if x1 == "void":
        print("Illegal type of void.")
        sys.exit()
    count_params += 1


def define_function():
    global display, count_params, type_of_params, name_of_params, scope_vars, last_dynamic, function_output_type, last_dynamic
    nameFunction = ""
    second = False
    nameParent = "global"
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, x) = scope_vars[j]
        if type == "function" and x is None:
            if not second:
                nameFunction = name
                second = True
            else:
                nameParent = name
                break
    activation = static_activation(nameFunction, count_params, type_of_params, display[nameParent], function_output_type)
    display[nameFunction] = activation

    last_dynamic = display[nameFunction].dynamic_finder()
    param_address = last_dynamic.parameters_address
    for j in range(count_params):
        add_variable(name_of_params[j], type_of_params[j], param_address[j])

    count_params = 0
    type_of_params = []
    name_of_params = []


def return_func():
    global index, PB, scope_vars, ss, last_dynamic, last_return_value_address, last_return_type
    last_return_value_address = last_dynamic.return_func(ss[-1])
    del ss[-1]
    del type_stack[-1]
    last_return_type = "int"


def return_nothing():
    global index, PB, scope_vars, ss, last_dynamic, last_return_value_address, last_return_type
    last_return_value_address = last_dynamic.return_func(0)
    last_return_type = "void"


def function_finish():
    global index, PB, scope_vars, ss, last_dynamic, last_return_value_address, last_return_type
    last_return_value_address = last_dynamic.return_func(0)
    last_return_type = "void"


def new_scope():
    global index
    add_scope("", "", index)


def exit_scope():
    global scope_vars
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, n1, n2, n3) = scope_vars[j]
        if n3 is None:
            del scope_vars[j]
            # scope_vars.remove(scope_vars[j])
            return
        else:
            del scope_vars[j]
            # scope_vars.remove(scope_vars[j])


def check_loop_scope():
    global index, scope_vars, PB
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "loop":
            PB[index] = "(JP, {}, , )".format(start_i)
            index += 1
            return
    print("No 'while' found for 'continue'.")
    sys.exit()


def check_break_scope():
    global index, scope_vars, PB, level_of_break
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "loop" or type == "switch":
            pb_of_breaks.append((index, level_of_break))
            index += 1
            return
    print("No 'while' or 'switch' found for 'break'.")
    sys.exit()


def jpf_save1():
    global index, scope_vars, PB
    saved_pbs.append(index)
    index += 1


def jp_save2():
    global index, scope_vars, PB
    saved_pbs.append(index)
    index += 1


def fill_save1():
    global index, scope_vars, PB
    x = saved_pbs[-2]
    PB[x] = "(JPF, {}, {}, )".format(ss[-1], index)
    del saved_pbs[-2]
    # saved_pbs.remove(saved_pbs[-2])
    del ss[-1]
    # ss.remove(ss[-1])
    del type_stack[-1]


def fill_save2():
    global index, scope_vars, PB
    x = saved_pbs[-1]
    PB[x] = "(JP, {}, , )".format(index)
    del saved_pbs[-1]
    # saved_pbs.remove(saved_pbs[-1])


def new_loop_scope():
    global index, scope_vars, PB, level_of_break
    add_scope("", "loop", index)
    level_of_break += 1


def exit_loop_scope():
    global index, scope_vars, PB, level_of_break, pb_of_breaks
    temp = []
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "loop":
            del scope_vars[j]
            # scope_vars.remove(scope_vars[j])
            for k in range(len(pb_of_breaks)):
                (idx, lev) = pb_of_breaks[k]
                if lev == level_of_break:
                    PB[idx] = "(JP, {}, , )".format(index)
                else:
                    temp.append(pb_of_breaks[k])
            pb_of_breaks = temp
            level_of_break -= 1
            return
        else:
            del scope_vars[j]
            # scope_vars.remove(scope_vars[j])


def label():
    global index, scope_vars, PB
    labels.append(index)


def jpf_save3():
    global index, scope_vars, PB
    saved_pbs.append(index)
    index += 1


def jp_label():
    global index, scope_vars, PB
    x = labels[-1]
    PB[index] = "(JP, {}, , )".format(x)
    index += 1
    del labels[-1]
    # labels.remove(labels[-1])


def fill_save3():
    global index, scope_vars, PB
    x = saved_pbs[-1]
    PB[x] = "(JPF, {}, {}, )".format(ss[-1], index)
    del saved_pbs[-1]
    # saved_pbs.remove(saved_pbs[-1])
    del ss[-1]
    # ss.remove(ss[-1])
    del type_stack[-1]


def cmp_save_case():
    global index, scope_vars, PB
    saved_pbs.append(index)
    index += 2


def fill_save_case():
    global index, scope_vars, PB, constants
    x = saved_pbs[-1]
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    PB[x] = "(EQ, {}, #{}, {})".format(ss[-1], constants[-1], t)
    PB[x+1] = "(JPF, {}, {}, )".format(t, index)
    del saved_pbs[-1]
    # saved_pbs.remove(saved_pbs[-1])
    del constants[-1]
    # constants.remove(constants[-1])


def new_break_scope():
    global index, scope_vars, PB, level_of_break
    add_scope("", "switch", index)
    level_of_break += 1


def exit_break_scope():
    global index, scope_vars, PB, level_of_break, pb_of_breaks
    temp = []
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, start_i, n) = scope_vars[j]
        if type == "switch":
            del scope_vars[j]
            print("#$%#^$%&$%@#@!#$@$#%$%^#$@!#@!#", level_of_break, len(pb_of_breaks))
            # scope_vars.remove(scope_vars[j])
            for k in range(len(pb_of_breaks)):
                (idx, lev) = pb_of_breaks[k]
                if lev == level_of_break:
                    PB[idx] = "(JP, {}, , )".format(index)
                else:
                    temp = pb_of_breaks[k]
            pb_of_breaks = temp
            level_of_break -= 1
            return
        else:
            del scope_vars[j]
            # scope_vars.remove(scope_vars[j])


def pop_expression():
    global index, scope_vars, PB, ss
    del ss[-1]
    # ss.remove(ss[-1])
    del type_stack[-1]


def run_next_case():
    global index, scope_vars, PB
    PB[index] = "(JP, {}, , )".format(index+3)
    index += 1


def two_useless():
    global index, scope_vars, PB
    t = get_temp_addr()
    PB[index] = "(EQ, {}, {}, {})".format(t, t, t)
    index += 1
    PB[index] = "(EQ, {}, {}, {})".format(t, t, t)
    index += 1


def push_id():
    global scope_vars, ss
    _, unknown_name, _ = tokens_received[-2]
    print("&&&&&&&&&&"+unknown_name)
    print(scope_vars)
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, address, num) = scope_vars[j]
        if name == unknown_name:
            ss.append(address)
            type_stack.append(type)
            return
    print("'" + unknown_name + "' is not defined.")
    sys.exit()


def push_id2():
    global scope_vars, ss
    _, unknown_name, _ = tokens_received[-3]
    for j in range(len(scope_vars) - 1, 0, -1):
        (name, type, address, num) = scope_vars[j]
        if name == unknown_name:
            ss.append(address)
            type_stack.append(type)
            return
    print("'" + unknown_name + "' is not defined.")
    sys.exit()


def assign():
    global index, PB, ss
    print(ss)
    print(type_stack)
    if type_stack[-1] == type_stack[-2]:
        a, b, c = translate_two_indirect_address(ss[-1], ss[-2], "")
        PB[index] = "(ASSIGN, {}, {}, )".format(a, b)
        index += 1
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
    else:
        print("Type mismatch in operands.")
        sys.exit()


def push_constant():
    global index, PB, ss
    print("ASDASDASD")
    _, number, _ = tokens_received[-2]
    t = get_temp_addr()
    # try:
    PB[index] = "(ASSIGN, #{}, {}, )".format(int(number), t)
    # except ValueError:
        # print(tokens_received[-1], tokens_received[-2], tokens_received[-3])
    index += 1
    ss.append(t)
    type_stack.append("int")


def push_constant2():
    global index, PB, ss, constants
    _, number, _ = tokens_received[-2]
    constants.append(int(number))


def callee_function_detection():
    global index, callee_static, callee_name
    _, tmp_name, _ = tokens_received[-3]
    callee_name.append(tmp_name)
    callee_static.append(display[callee_name[-1]])
    # callee_static =


def add_argument():
    global ss, index, arguments, count_arguments
    print(ss)
    arguments.append(ss[-1])
    count_arguments += 1
    del ss[-1]
    del type_stack[-1]


def check_number_of_arguments():
    global arguments, count_arguments, callee_static
    print("@@@@@@@@@@@@@@@" + str(count_arguments), arguments)
    print(callee_static[-1].num_of_parameters)

    if count_arguments == callee_static[-1].num_of_parameters:
        return
    print("Mismatch in numbers of arguments of '" + callee_static[-1].name + "'")
    sys.exit()


def call():
    global arguments, count_arguments, callee_static, index, PB, last_dynamic
    type_param = callee_static[-1].type_of_parameters
    for j in range(len(type_param)):
        if len(type_param) == 1 and type_param[0] == "void":
            break
        if not type_param[j].__contains__("[]"):
            if is_dynamic():
                t = last_dynamic.get_pseudo_dynamic_temp_addr()
            else:
                t = get_temp_addr()
            PB[index] = "(ASSIGN, {}, {}, )".format(arguments[j], t)
            index += 1
            arguments[j] = t
    callee_dynamic = dynamic_activation(callee_static[-1], arguments, None, index + callee_static[-1].num_of_parameters + 4 + 1, False, None)
    ss.append(callee_dynamic.return_value_address)
    type_stack.append(callee_static[-1].output_type)
    arguments = []
    count_arguments = 0
    # add_scope(callee_name, "function", callee_static.start_line)
    PB[index] = "(JP, {}, , )".format(callee_static[-1].start_line)
    index += 1


def push_return_value_address():
    return
#     global index, last_return_value_address, scope_vars, las
#     ss.append(last_return_value_address)
#     type_stack.append(last_return_type)
#     for j in range(len(scope_vars)-1, 0, -1):
#         (name, type, start_i, n) = scope_vars[j]
#         if type == "function" and n is None:
#             del scope_vars[j]
#             # scope_vars.remove(scope_vars[j])
#             return
#         del scope_vars[j]
#         # scope_vars.remove(scope_vars[j])


def get_back_to_caller():
    global index, callee_static, last_dynamic
    name = ""
    type = ""
    start_i = ""
    n = 0
    print(scope_vars)
    for j in range(len(scope_vars)-1, 0, -1):
        print(scope_vars)
        (name, type, start_i, n) = scope_vars[j]
        if type == "function" and n is None:
            print(scope_vars)
            break
    last_dynamic = display[name].dynamic_finder()
    print(scope_vars)
    del callee_static[-1]
    del callee_name[-1]


def push_array_element():
    global index, PB, ss, last_dynamic
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    if type_stack[-1] == "int":
        PB[index] = "(MULT, {}, #4, {})".format(ss[-1], t)
        index += 1
        PB[index] = "(ADD, {}, {}, {})".format(ss[-2], t, t)
        index += 1
        # PB[index] = "(ASSIGN, @{}, {}, )".format(t, t)
        # index += 1
        del ss[-2]
        # ss.remove(ss[-2])
        del type_stack[-2]
        # type_stack.remove(type_stack[-2])
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
        ss.append("@" + str(t))
        type_stack.append("int")
    else:
        print("Error! Index is not int")
        sys.exit()


def negative():
    global index, PB, ss
    a, b, c = translate_two_indirect_address(ss[-1], ss[-1], "")
    PB[index] = "(SUB, #0, {}, {})".format(a, b)
    index += 1


def mult():
    global index, PB, ss, last_dynamic
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    if type_stack[-2] == type_stack[-1] == "int":
        a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
        PB[index] = "(MULT, {}, {}, {})".format(a, b, c)
        index += 1
        del ss[-2]
        # ss.remove(ss[-2])
        del type_stack[-2]
        # type_stack.remove(type_stack[-2])
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
        ss.append(t)
        type_stack.append("int")
    else:
        print("Type mismatch in operands.")
        sys.exit()


def add():
    global index, PB, ss, last_dynamic
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    if type_stack[-2] == type_stack[-1] == "int":
        a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
        PB[index] = "(ADD, {}, {}, {})".format(a, b, c)
        index += 1
        del ss[-2]
        # ss.remove(ss[-2])
        del type_stack[-2]
        # type_stack.remove(type_stack[-2])
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
        ss.append(t)
        type_stack.append("int")
    else:
        print("Type mismatch in operands.")
        sys.exit()


def set_sign_positive():
    global last_sign
    last_sign = "positive"


def set_sign_negative():
    global last_sign
    last_sign = "negative"


def add_signed():
    global index, PB, ss, last_sign, last_dynamic
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    if type_stack[-2] == type_stack[-1] == "int":
        if last_sign == "negative":
            a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
            PB[index] = "(SUB, {}, {}, {})".format(a, b, c)
        else:
            a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
            PB[index] = "(ADD, {}, {}, {})".format(a, b, c)
        index += 1
        del ss[-2]
        # ss.remove(ss[-2])
        del type_stack[-2]
        # type_stack.remove(type_stack[-2])
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
        ss.append(t)
        type_stack.append("int")
    else:
        print("Type mismatch in operands.")
        sys.exit()


def set_condition_less():
    global last_condition
    last_condition = "less"


def set_condition_equal():
    global last_condition
    last_condition = "equal"


def check_condition():
    global index, PB, ss, last_dynamic
    if is_dynamic():
        t = last_dynamic.get_pseudo_dynamic_temp_addr()
    else:
        t = get_temp_addr()
    if type_stack[-2] == type_stack[-1] == "int":
        if last_condition == "less":
            a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
            PB[index] = "(LT, {}, {}, {})".format(a, b, c)
        else:
            a, b, c = translate_two_indirect_address(ss[-2], ss[-1], t)
            PB[index] = "(EQ, {}, {}, {})".format(a, b, c)
        index += 1
        del ss[-2]
        # ss.remove(ss[-2])
        del type_stack[-2]
        # type_stack.remove(type_stack[-2])
        del ss[-1]
        # ss.remove(ss[-1])
        del type_stack[-1]
        # type_stack.remove(type_stack[-1])
        ss.append(t)
        type_stack.append("int")
    else:
        print("Type mismatch in operands.")
        sys.exit()


def initializer():
    global index, PB, last_dynamic, callee_static, last_return_type, last_return_value_address, callee_name
    have_main = False
    line_of_first_assignment = None
    main_func = ""

    # save = index
    # index += 1

    for f in display:
        if f == "global":
            continue
        if line_of_first_assignment is None:
            line_of_first_assignment = index
        PB[index] = "(ASSIGN, #0, {}, )".format(display[f].recurrent_counter_address)
        index += 1

    PB[index] = "(ASSIGN, #0, 0, )"
    index += 1

    for l in saved_arrays_declaration_pbs:
        PB[index] = l
        index += 1

    for f in display:
        if f == "main" and display[f].num_of_parameters == 0 and len(display[f].type_of_parameters) > 0 and display[f].type_of_parameters[0] == "void" and display[f].output_type == "void":
            have_main = True
            main_func = f
            PB[0] = "(JP, {}, , )".format(line_of_first_assignment)
            break

    if not have_main:
        print("main function not found!")
        sys.exit()

    callee_static.append(display[main_func])
    callee_dynamic = dynamic_activation(callee_static[-1], arguments, None, index + callee_static[-1].num_of_parameters + 4 + 1, False, None)
    ss.append(callee_dynamic.return_value_address)
    type_stack.append(callee_static[-1].output_type)
    add_scope(main_func, "function", callee_static[-1].start_line)
    PB[index] = ("(JP, {}, , )".format(display[main_func].start_line))
    index += 1


def semantic_routine(action):
    print("&*************************" + str(len(constants)))
    if action == "#DECLARE_VARIABLE":
        declare_variable()
    elif action == "#DECLARE_ARRAY":
        declare_array()
    elif action == "#FUNCTION_SCOPE":
        function_scope()
    elif action == "#END_FUNCTION_SCOPE":
        end_function_scope()
    elif action == "#PARAM_VOID":
        param_void()
    elif action == "#PARAM_VARIABLE":
        param_variable()
    elif action == "#PARAM_ARRAY":
        param_array()
    elif action == "#DEFINE_FUNCTION":
        define_function()
    elif action == "#RETURN_FUNC":
        return_func()
    elif action == "#RETURN_NOTHING":
        return_nothing()
    elif action == "#NEW_SCOPE":
        new_scope()
    elif action == "#EXIT_SCOPE":
        exit_scope()
    elif action == "#CHECK_LOOP_SCOPE":
        check_loop_scope()
    elif action == "#CHECK_BREAK_SCOPE":
        check_break_scope()
    elif action == "#JPF_SAVE1":
        jpf_save1()
    elif action == "#JP_SAVE2":
        jp_save2()
    elif action == "#FILL_SAVE1":
        fill_save1()
    elif action == "#FILL_SAVE2":
        fill_save2()
    elif action == "#NEW_LOOP_SCOPE":
        new_loop_scope()
    elif action == "#EXIT_LOOP_SCOPE":
        exit_loop_scope()
    elif action == "#LABEL":
        label()
    elif action == "#JPF_SAVE3":
        jpf_save3()
    elif action == "#JP_LABEL":
        jp_label()
    elif action == "#FILL_SAVE3":
        fill_save3()
    elif action == "#CMP_SAVE_CASE":
        cmp_save_case()
    elif action == "#FILL_SAVE_CASE":
        fill_save_case()
    elif action == "#POP_EXPRESSION":
        pop_expression()
    elif action == "#RUN_NEXT_CASE":
        run_next_case()
    elif action == "#TWO_USELESS":
        two_useless()
    elif action == "#PUSH_ID":
        push_id()
    elif action == "#ASSIGN":
        assign()
    elif action == "#PUSH_CONSTANT":
        push_constant()
    elif action == "#CALLEE_FUNCTION_DETECTION":
        callee_function_detection()
    elif action == "#ADD_ARGUMENT":
        add_argument()
    elif action == "#CHECK_NUMBER_OF_ARGUMENTS":
        check_number_of_arguments()
    elif action == "#CALL":
        call()
    elif action == "#PUSH_RETURN_VALUE_ADDRESS":
        push_return_value_address()
    elif action == "#GET_BACK_TO_CALLER":
        get_back_to_caller()
    elif action == "#PUSH_ARRAY_ELEMENT":
        push_array_element()
    elif action == "#NEGATIVE":
        negative()
    elif action == "#MULT":
        mult()
    elif action == "#ADD":
        add()
    elif action == "#SET_SIGN_POSITIVE":
        set_sign_positive()
    elif action == "#SET_SIGN_NEGATIVE":
        set_sign_negative()
    elif action == "#ADD_SIGNED":
        add_signed()
    elif action == "#SET_CONDITION_LESS":
        set_condition_less()
    elif action == "#SET_CONDITION_EQUAL":
        set_condition_equal()
    elif action == "#CHECK_CONDITION":
        check_condition()
    elif action == "#PUSH_ID2":
        push_id2()
    elif action == "#PUSH_CONSTANT2":
        push_constant2()
    elif action == "#NEW_BREAK_SCOPE":
        new_break_scope()
    elif action == "#EXIT_BREAK_SCOPE":
        exit_break_scope()
    elif action == "#INITIALIZER":
        initializer()
    elif action == "#FUNCTION_FINISH":
        function_finish()
