import re
import sys
import argparse
import xml.etree.ElementTree as ET


class Interpret:
    input_file = None
    source_file = None
    labels = []

    opcode_list = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN',
                   'PUSHS', 'POPS', 'ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT',
                   'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR',
                   'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK']

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--source', nargs=1, help='Input file name')
        parser.add_argument('--input', nargs=1, help='Input file name')
        args = vars(parser.parse_args())
        if args['input']:
            Interpret.input_file = open(args['input'][0], 'r')
        else:
            Interpret.input_file = None

        if args['source']:
            Interpret.source_file = args['source'][0]
        else:
            Interpret.source_file = None

        return Interpret.source_file

    @staticmethod
    def load_xml():
        file = Interpret.parse_args()
        if (file):
            try:
                tree = ET.parse(file)
            except ET.ParseError:
                sys.exit(31)
        else:
            try:
                tree = ET.parse(sys.stdin)
            except ET.ParseError:
                sys.exit(31)
        root = tree.getroot()
        return root

    @staticmethod
    def check_duplicit_order(values):
        return len(set(values)) == len(values)

    @staticmethod
    def interpret():
        root = Interpret.load_xml()
        order_values = []
        label = None
        jump = False
        if (root.tag != 'program' or root.attrib['language'] != 'IPPcode23'):
            sys.exit(32)
        for element in root:
            if ('order' not in element.attrib or 'opcode' not in element.attrib):
                sys.exit(32)
            if (element.attrib['opcode'].upper() not in Interpret.opcode_list):
                sys.exit(32)
            if (element.tag != 'instruction' or
                    element.attrib['order'].isdigit() == False or
                    int(element.attrib['order']) < 1):
                sys.exit(32)
            order_values.append(element.attrib['order'])
            if (element.attrib['opcode'].upper() == 'LABEL'):
                Interpret.labels.append(element[0].text)
        if (Interpret.check_duplicit_order(order_values) == False):
            sys.exit(32)
        # check for duplicate labels
        if (len(Interpret.labels) != len(set(Interpret.labels))):
            sys.exit(52)
        root = sorted(root, key=lambda e: int(e.get('order')))
        for inst in root:
            if (inst.attrib['opcode'].upper() == 'JUMP'):
                label = inst[0].text
                if (label not in Interpret.labels):
                    sys.exit(52)
                jump = True
                continue

            if (jump):
                if (inst.attrib['opcode'].upper() == 'LABEL'):
                    if (inst[0].text == label):
                        instruction = Instruction(inst, inst.attrib['opcode'])
                        instruction.process_instruction()
                        jump = False
                    else:
                        continue
                else:
                    continue
            else:
                instruction = Instruction(inst, inst.attrib['opcode'])
                instruction.process_instruction()


class Instruction:
    data_stack = []

    def __init__(self, inst, opcode):
        try:
            self.inst = sorted(inst, key=lambda e: int(re.compile(r'^arg(\d+)$').match(e.tag).group(1)))
        except AttributeError:
            sys.exit(32)
        self.opcode = opcode
        self.args = []
        Instruction.check_arg_tag(self.inst)
        for arg in self.inst:
            self.args.append(self.get_type(arg))

    @staticmethod
    def check_arg_count(args, arg_count):
        if (len(args) != arg_count):
            sys.exit(32)

    @staticmethod
    def check_arg_tag(args):
        if (len(args) == 1):
            if (args[0].tag != 'arg1'):
                sys.exit(32)
        elif (len(args) == 2):
            if (args[0].tag != 'arg1' or args[1].tag != 'arg2'):
                sys.exit(32)
        elif (len(args) == 3):
            if (args[0].tag != 'arg1' or args[1].tag != 'arg2' or args[2].tag != 'arg3'):
                sys.exit(32)

    def process_instruction(self):

        match self.opcode.upper():
            case 'MOVE':
                Instruction.check_arg_count(self.args, 2)
                if (isinstance(self.args[0], Var)):
                    FrameModel.init_var(self.args[0].name, self.args[1])
                else:
                    sys.exit(32)
            case 'CREATEFRAME':
                FrameModel.TF = dict()
            case 'POPFRAME':
                if (FrameModel.LF == None):
                    sys.exit(55)
                FrameModel.TF = FrameModel.stack.pop()
                FrameModel.LF = FrameModel.stack[-1]
            case 'PUSHFRAME':
                if (FrameModel.TF == None):
                    sys.exit(55)
                FrameModel.stack.append(FrameModel.TF)
                FrameModel.LF = FrameModel.stack[-1]
                FrameModel.TF = None
            case 'DEFVAR':
                Instruction.check_arg_count(self.args, 1)
                FrameModel.add_to_frame(self.args[0].name)
            case 'CALL':
                pass
            case 'RETURN':
                pass
            case 'PUSHS':
                Instruction.check_arg_count(self.args, 1)
                if (isinstance(self.args[0], Symb)):
                    Instruction.data_stack.append(self.args[0].value)
                elif (isinstance(self.args[0], Var)):
                    Instruction.data_stack.append(FrameModel.get_value(self.args[0].name))
                else:
                    sys.exit(32)
            case 'POPS':
                Instruction.check_arg_count(self.args, 1)
                if (isinstance(self.args[0], Var)):
                    if (len(Instruction.data_stack) > 0):
                        FrameModel.set_value(self.args[0].name, Instruction.data_stack.pop())
                    else:
                        sys.exit(56)
                else:
                    sys.exit(32)
            case 'ADD':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.add(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.add(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.add(self.args[0], FrameModel.get_value(self.args[1].name),
                                        FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.add(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'SUB':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.sub(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.sub(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.sub(self.args[0], FrameModel.get_value(self.args[1].name),
                                        FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.sub(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'MUL':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.mul(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.mul(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.mul(self.args[0], FrameModel.get_value(self.args[1].name),
                                        FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.mul(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'IDIV':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.idiv(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.idiv(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.idiv(self.args[0], FrameModel.get_value(self.args[1].name),
                                         FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.idiv(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'LT':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.lt(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.lt(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.lt(self.args[0], FrameModel.get_value(self.args[1].name),
                                       FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.lt(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'GT':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.gt(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.gt(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.gt(self.args[0], FrameModel.get_value(self.args[1].name),
                                       FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.gt(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'EQ':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.eq(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.eq(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.eq(self.args[0], FrameModel.get_value(self.args[1].name),
                                       FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.eq(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'AND':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction._and(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction._and(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction._and(self.args[0], FrameModel.get_value(self.args[1].name),
                                         FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction._and(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'OR':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction._or(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction._or(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction._or(self.args[0], FrameModel.get_value(self.args[1].name),
                                        FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction._or(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'NOT':
                Instruction.check_arg_count(self.args, 2)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var)):
                        Instruction._not(self.args[0], FrameModel.get_value(self.args[1].name))
                    elif (isinstance(self.args[1], Symb)):
                        Instruction._not(self.args[0], self.args[1].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'INT2CHAR':
                Instruction.check_arg_count(self.args, 2)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var)):
                        Instruction.int2char(self.args[0], FrameModel.get_value(self.args[1].name))
                    elif (isinstance(self.args[1], Symb)):
                        Instruction.int2char(self.args[0], self.args[1].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'STRI2INT':
                Instruction.check_arg_count(self.args, 3)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var) and isinstance(self.args[2], Symb)):
                        Instruction.stri2int(self.args[0], FrameModel.get_value(self.args[1].name), self.args[2].value)
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Var)):
                        Instruction.stri2int(self.args[0], self.args[1].value, FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Var) and isinstance(self.args[2], Var)):
                        Instruction.stri2int(self.args[0], FrameModel.get_value(self.args[1].name),
                                             FrameModel.get_value(self.args[2].name))
                    elif (isinstance(self.args[1], Symb) and isinstance(self.args[2], Symb)):
                        Instruction.stri2int(self.args[0], self.args[1].value, self.args[2].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'READ':
                Instruction.check_arg_count(self.args, 2)
                if (isinstance(self.args[0], Var)):
                    Instruction.read(self.args[0], self.args[1])
                else:
                    sys.exit(32)
            case 'WRITE':
                Instruction.check_arg_count(self.args, 1)
                if (isinstance(self.args[0], Var)):
                    print(FrameModel.get_value(self.args[0].name), end='')
                elif (isinstance(self.args[0], Symb)):
                    print(self.args[0].value, end='')
                else:
                    sys.exit(32)
            case 'CONCAT':
                pass
            case 'STRLEN':
                pass
            case 'GETCHAR':
                pass
            case 'SETCHAR':
                pass
            case 'TYPE':
                Instruction.check_arg_count(self.args, 2)
                if (isinstance(self.args[0], Var)):
                    if (isinstance(self.args[1], Var)):
                        Instruction._type(self.args[0], FrameModel.get_value(self.args[1].name))
                    elif (isinstance(self.args[1], Symb)):
                        Instruction._type(self.args[0], self.args[1].value)
                    else:
                        sys.exit(32)
                else:
                    sys.exit(32)
            case 'LABEL':
                pass
            case 'JUMP':
                pass
            case 'JUMPIFEQ':
                pass
            case 'JUMPIFNEQ':
                pass
            case 'EXIT':
                Instruction.check_arg_count(self.args, 1)
                if (isinstance(self.args[0], Var)):
                    Instruction.exit(FrameModel.get_value(self.args[0].name))
                elif (isinstance(self.args[0], Symb)):
                    Instruction.exit(self.args[0].value)
                else:
                    sys.exit(32)
            case 'DPRINT':
                pass
            case 'BREAK':
                pass
            case 'LABEL':
                pass

    @staticmethod
    def get_type(arg):
        if (arg.attrib['type'] == 'var'):
            return Var(arg.text)
        elif (arg.attrib['type'] in ['int', 'string', 'bool', 'nil']):
            return Symb(arg)
        elif (arg.attrib['type'] == 'label'):
            return Label(arg.text)
        elif (arg.attrib['type'] == 'type'):
            return arg.text

    @staticmethod
    def add(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int):
            FrameModel.set_value(var.name, int(symb1 + symb2))
        else:
            sys.exit(53)

    @staticmethod
    def sub(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int):
            FrameModel.set_value(var.name, int(symb1 - symb2))
        else:
            sys.exit(53)

    @staticmethod
    def mul(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int):
            FrameModel.set_value(var.name, int(symb1 * symb2))
        else:
            sys.exit(53)

    @staticmethod
    def idiv(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int):
            if (int(symb2) == 0):
                sys.exit(57)
            else:
                FrameModel.set_value(var.name, int(symb1 // symb2))
        else:
            sys.exit(53)

    @staticmethod
    def lt(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int or
                type(symb1) == bool and type(symb2) == bool or
                type(symb1) == str and type(symb2) == str):
            FrameModel.set_value(var.name, symb1 < symb2)
        else:
            sys.exit(53)

    @staticmethod
    def gt(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int or
                type(symb1) == bool and type(symb2) == bool or
                type(symb1) == str and type(symb2) == str):
            FrameModel.set_value(var.name, symb1 > symb2)
        else:
            sys.exit(53)

    @staticmethod
    def eq(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == int or
                type(symb1) == bool and type(symb2) == bool or
                type(symb1) == str and type(symb2) == str or
                type(symb1) == ''):
            FrameModel.set_value(var.name, symb1 == symb2)
        else:
            sys.exit(53)

    @staticmethod
    def _and(var, symb1, symb2):
        if (type(symb1) == bool and type(symb2) == bool):
            FrameModel.set_value(var.name, symb1 and symb2)
        else:
            sys.exit(53)

    @staticmethod
    def _or(var, symb1, symb2):
        if (type(symb1) == bool and type(symb2) == bool):
            FrameModel.set_value(var.name, symb1 or symb2)
        else:
            sys.exit(53)

    @staticmethod
    def _not(var, symb):
        if (type(symb) == bool):
            FrameModel.set_value(var.name, not symb)
        else:
            sys.exit(53)

    @staticmethod
    def int2char(var, symb):
        if (type(symb) == int):
            try:
                FrameModel.set_value(var.name, chr(symb))
            except ValueError:
                sys.exit(58)
        else:
            sys.exit(53)

    @staticmethod
    def stri2int(var, symb1, symb2):
        if (type(symb1) == str and type(symb2) == int):
            if (symb2 > len(symb1) - 1 or symb2 < 0):
                sys.exit(58)
            else:
                FrameModel.set_value(var.name, ord(symb1[symb2]))
        else:
            sys.exit(53)

    @staticmethod
    def read(var, _type):

        if (Interpret.input_file):
            value = Interpret.input_file.readline()
        else:
            value = input()

        if (_type == 'int'):
            FrameModel.set_value(var.name, int(value))
        elif (_type == 'string'):
            FrameModel.set_value(var.name, str(value).rstrip('\n'))
        elif (_type == 'bool'):
            if (value.lower() == 'true'):
                FrameModel.set_value(var.name, 'true')
            else:
                FrameModel.set_value(var.name, 'false')
        else:
            sys.exit(32)

    @staticmethod
    def concat(var, symb1, symb2):
        if (type(symb1) == str and type(symb2) == str):
            FrameModel.set_value(var.name, symb1 + symb2)
        else:
            sys.exit(53)

    @staticmethod
    def strlen(var, symb):
        if (type(symb) == str):
            FrameModel.set_value(var.name, len(symb))
        else:
            sys.exit(53)

    @staticmethod
    def getchar(var, symb1, symb2):
        if (type(symb1) == str and type(symb2) == int):
            if (symb2 > len(symb1) - 1 or symb2 < 0):
                sys.exit(58)
            else:
                FrameModel.set_value(var.name, symb1[symb2])
        else:
            sys.exit(53)

    @staticmethod
    def setchar(var, symb1, symb2):
        if (type(symb1) == int and type(symb2) == str):
            FrameModel.set_value(var.name, var.name[:symb1] + symb2 + var.name[symb1 + 1:])
        else:
            sys.exit(53)

    @staticmethod
    def exit(symb):
        if (type(symb) == int):
            if (0 <= symb <= 49):
                sys.exit(symb)
            else:
                sys.exit(57)
        else:
            sys.exit(53)

    @staticmethod
    def _type(var, symb):

        if (symb == None):
            FrameModel.set_value(var.name, '')

        if (type(symb) == int):
            FrameModel.set_value(var.name, 'int')
        elif (type(symb) == bool):
            FrameModel.set_value(var.name, 'bool')
        elif (type(symb) == str):
            if (symb == ''):
                FrameModel.set_value(var.name, 'nil')
            else:
                FrameModel.set_value(var.name, 'string')


class FrameModel:
    GF = dict()
    LF = None
    TF = None
    stack = []

    @classmethod
    def add_to_frame(cls, var):
        frame = cls.get_frame(var)

        if (frame == None):
            sys.exit(55)

        if (var[3:] in frame):
            sys.exit(52)

        frame[var[3:]] = None

    @classmethod
    def get_frame(cls, var):
        if (var[:2] == 'LF'):
            return cls.LF
        elif (var[:2] == 'GF'):
            return cls.GF
        elif (var[:2] == 'TF'):
            return cls.TF
        else:
            sys.exit(57)

    @classmethod
    def is_defined(cls, var):
        frame = cls.get_frame(var)
        if (frame == None):
            sys.exit(55)
        if (var[3:] in frame):
            return True
        else:
            return False

    @classmethod
    def get_value(cls, var):
        if (cls.is_defined(var) == False):
            sys.exit(54)
        frame = cls.get_frame(var)
        return frame[var[3:]]

    @classmethod
    def set_value(cls, var, value):
        if (cls.is_defined(var) == False):
            sys.exit(54)
        frame = cls.get_frame(var)
        frame[var[3:]] = value

    @classmethod
    def init_var(cls, l_val, r_val):

        if (cls.is_defined(l_val) == False):
            sys.exit(54)

        frame_l_val = cls.get_frame(l_val)  # v ktorom frame sa nachadza premenna ktoru chceme inicializovat

        if (isinstance(r_val, Var)):  # ak je r-hodnota premenna
            r_val = r_val.name
            if (cls.is_defined(r_val) == False):
                sys.exit(54)

            frame_r_val = cls.get_frame(r_val)
            frame_l_val[l_val[3:]] = frame_r_val[r_val[3:]]

        if (isinstance(r_val, Symb)):  # ak je r-hodnota konstanta
            frame_l_val[l_val[3:]] = r_val.value


class Var:

    def __init__(self, name):
        self.name = name


class Symb:

    def __init__(self, arg):
        self.arg = arg
        self.value = self.cast_value()

    def cast_value(self):

        match self.arg.attrib['type']:
            case 'string':
                esc_sequences = list(set(re.findall(r"\\[0][0-9][0-9]", str(self.arg.text))))
                if (len(esc_sequences) > 0):
                    for element in esc_sequences:
                        formatted_string = str(self.arg.text).replace(element, chr(int(element[2:])))
                    return formatted_string
                else:
                    return str(self.arg.text)
            case 'int':
                try:
                    return int(self.arg.text)
                except ValueError:
                    sys.exit(32)
            case 'bool':
                if (self.arg.text.upper() == 'TRUE'):
                    return True
                elif (self.arg.text.upper() == 'FALSE'):
                    return False
                else:
                    sys.exit(32)
            case 'nil':
                return ''
            case _:
                sys.exit(32)


class Label:

    def __init__(self, name):
        self.name = name


# calls interpret
Interpret.interpret()
sys.exit(0)
