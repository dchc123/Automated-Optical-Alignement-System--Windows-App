"""
| $Revision:: 278910                                   $:  Revision of last commit
| $Author:: sfarsi@SEMNET.DOM                          $:  Author of last commit
| $Date:: 2018-07-06 01:01:42 +0100 (Fri, 06 Jul 2018) $:  Date of last commit
| --------------------------------------------------------------------------------

"""
from CLI.Utilities.excel_parser import ExcelParser
import os
import re
from operator import attrgetter
import textwrap


class RegisterMapBank(object):
    def __init__(self):

        self.bank_name = ""
        self.registers = {}
        self.sorted_registers = None


class RegisterMapRegister(object):
    def __init__(self):
    
        self.parent_bank = None

        self.register_name = ""
        self.address = 0
        self.child_parameters = {}

    def calculate_reset_value(self):
        
        reset_value = 0
        
        for parameter in self.child_parameters.values():
            reset_value = reset_value | (parameter.reset_value << parameter.low_bit)
            
        return reset_value

    def update_reset_value(self, reset_value=0):

        for parameter in self.child_parameters.values():
            mask = (1 << (parameter.high_bit + 1)) - 1
            parameter.reset_value = (reset_value & mask) >> parameter.low_bit
        

class RegisterMapParameter(object):
    def __init__(self):
    
        self.parent_register = None
        
        self.parameter_name = ""
        self.high_bit = 0
        self.low_bit = 0
        self.description = ""
        self.reset_value = 0


class RegisterMap(object):
    def __init__(self):
    
        self.register_banks = {}
        self.pseudo_csr_offset = 0
        
    @staticmethod
    def parse_bit_slice(bit_slice):
        if ':' in bit_slice:
            sep = bit_slice.split(':')
            return int(sep[0]), int(sep[1])
        else:
            return int(bit_slice), int(bit_slice)
        
    def get_register_information(self, register_name, final_bank):
        register = self.find_register(register_name, final_bank)

        if register is None:
            raise ValueError("Register %s could not be found." % register_name)

        return {
            "Type": "Register",
            "Address": register.address,
            "Reset": register.calculate_reset_value(),
            "Self": register
        }

    def get_parameter_information(self, parameter_name, final_bank):

        parameter = self.find_parameter(parameter_name, final_bank)
        if parameter is None:
            raise ValueError("Parameter %s could not be found." % parameter_name)

        return {
            "Type": "Parameter",
            "Address": parameter.parent_register.address,
            "LowBit": parameter.low_bit,
            "HighBit": parameter.high_bit,
            "Description": parameter.description,
            "Reset": parameter.reset_value,
            "Self": parameter
        }

    @staticmethod
    def parse_bank_name(register):
        reg_parse = re.match('l(\d+)_\S+', register)

        if reg_parse is None:
            # This is a common register
            return "common"
        else:
            return int(reg_parse.groups()[0])

    def find_bank(self, bank_name):
        if bank_name not in self.register_banks.keys():
            return None

        return self.register_banks[bank_name]

    def find_register(self, register_name, bank_name):
        register_bank = self.find_bank(bank_name)
        register_list = register_bank.registers

        if register_name not in register_list.keys():
            return None

        return register_list[register_name]

    def find_parameter(self, parameter_name, bank_name):
        register_bank = self.find_bank(bank_name)
        register_list = register_bank.registers

        for register in register_list.values():
            for parameter_key in register.child_parameters.keys():
                if parameter_key == parameter_name:
                    return register.child_parameters[parameter_key]

        return None

    def find_register_by_address(self, address):
        for bank in self.register_banks.values():
            for register in bank.registers.values():
                if register.address == address:
                    return register

        return None

    def sort_register_banks(self):
        for bank in self.register_banks.values():
            if bank.sorted_registers is None:
                bank.sorted_registers = sorted(bank.registers.values(), key=attrgetter('address'))

    def parse_flat_register(self, register_name, address):
        bank_name = self.parse_bank_name(register_name)

        new_bank = self.find_bank(bank_name)
        if new_bank is None:
            new_bank = RegisterMapBank()
            new_bank.bank_name = bank_name
            self.register_banks[bank_name] = new_bank
        
        new_register = self.find_register(register_name, bank_name)
        if new_register is None:
            new_register = RegisterMapRegister()
            new_register.parent_bank = new_bank
            new_register.register_name = register_name
            new_register.address = address
            self.register_banks[bank_name].registers[register_name] = new_register

        return new_register
        
    def parse_flat_spreadsheet(self, filename, sheet):
        excel_parser = ExcelParser()
        excel_parser.open_file(filename)
        flat_map = excel_parser.read_excel_table("PARAMETER_NAME", sheet)
        
        for parameter_name in flat_map.keys():
            new_register = self.parse_flat_register(flat_map[parameter_name]["REGISTER_NAME"],
                                                    flat_map[parameter_name]["ADDRESS"])

            bit_slice = self.parse_bit_slice(flat_map[parameter_name]["BIT_SLICE"])

            new_parameter = RegisterMapParameter()
            new_parameter.parent_register = new_register
            new_parameter.parameter_name = parameter_name
            new_parameter.high_bit = bit_slice[0]
            new_parameter.low_bit = bit_slice[1]
            new_parameter.description = flat_map[parameter_name]["DESCRIPTION"]
            new_parameter.reset_value = int(flat_map[parameter_name]["RESET_VALUE"])

            new_register.child_parameters[parameter_name] = new_parameter
            
    def load_register_bank(self, prefix, filename, sheet):
        excel_parser = ExcelParser()
        excel_parser.open_file(filename)
        reg_map = excel_parser.read_excel_table("PARAMETER_NAME", sheet)
        
        for parameter in reg_map.keys():
        
            reg_name = prefix + reg_map[parameter]["REGISTER_NAME"]
            param_name = prefix + parameter
        
            new_register = self.parse_flat_register(reg_name, reg_map[parameter]["ADDRESS"])
        
            bit_slice = self.parse_bit_slice(reg_map[parameter]["BIT_SLICE"])
        
            new_parameter = RegisterMapParameter()
            new_parameter.parent_register = new_register
            new_parameter.parameter_name = param_name
            new_parameter.high_bit = bit_slice[0]
            new_parameter.low_bit = bit_slice[1]
            new_parameter.description = reg_map[parameter]["DESCRIPTION"]
            new_parameter.reset_value = int(reg_map[parameter]["RESET_VALUE"])

            new_register.child_parameters[param_name] = new_parameter

    def get_lane_registers(self, bank):
        registers_dict = {}
        parameters_dict = {}

        for register in self.find_bank(bank).registers:
            register_info = self.get_register_information(register, bank)
            register_name = re.sub(r'\w\d\w', '', register, 1)
            registers_dict.update({register_name: register_info})
            for param in self.find_bank(bank).registers[register].child_parameters:
                param_info = self.get_parameter_information(param, bank)
                param_name = re.sub(r'\w\d\w', '', param, 1)
                parameters_dict.update({param_name: param_info})

        full_dict = registers_dict.copy()
        full_dict.update(parameters_dict)
        return full_dict

    def get_global_registers(self, banks):
        registers_dict = {}
        parameters_dict = {}

        for bank in banks:
            for register in self.find_bank(bank).registers:
                register_info = self.get_register_information(register, bank)
                registers_dict.update({register: register_info})
                for param in self.find_bank(bank).registers[register].child_parameters:
                    param_info = self.get_parameter_information(param, bank)
                    parameters_dict.update({param: param_info})

        full_dict = registers_dict.copy()
        full_dict.update(parameters_dict)
        return full_dict

    @staticmethod
    def create_csr_class(file_name, csr_dict, class_name):
        with open(file_name, mode='w+', encoding='UTF-8') as outfile:
            outfile.write('from Core.base_device import BaseDeviceBlock\n'
                          '\n\nclass {}(BaseDeviceBlock):\n'.format(class_name))

            t = '    '

            outfile.write('\n{t}def __init__(self):\n'
                          '{t}{t}super().__init__()\n'
                          '{t}{t}self._read = None\n'
                          '{t}{t}self._write = None\n'
                          '{t}{t}self.name = None\n'
                          '{t}{t}self.logger = None\n'.format(t=t))

            for name in csr_dict.keys():
                a = csr_dict[name]['Address']
                r = csr_dict[name]['Reset']
                outfile.write('\n{t}@property\n'
                              '{t}def {n}(self):\n'.format(n=name, t=t))

                if csr_dict[name]['Type'] == 'Parameter':
                    hi = csr_dict[name]['HighBit']
                    lo = csr_dict[name]['LowBit']
                    d = textwrap.fill(csr_dict[name]['Description'], subsequent_indent='{t}{t}'.format(t=t), width=80)
                    outfile.write('{t}{t}"""\n'
                                  '{t}{t}{d}\n'
                                  '{t}{t}:value: {r}\n'
                                  '{t}{t}"""\n'
                                  '{t}{t}hi = {hi}\n'
                                  '{t}{t}lo = {lo}\n'
                                  '{t}{t}raw_value = self._read({a})\n'
                                  '{t}{t}mask = (((0x1 << (hi + 1)) - 1) >> lo) << lo\n'
                                  '{t}{t}value = (raw_value & mask) >> lo\n'
                                  '{t}{t}self.logger.debug("%s read from 0x%X[%d:%d] => %d"'
                                  ' % (self.name, {a}, hi, lo, value))\n'
                                  '{t}{t}return value\n'.format(t=t, a=a, d=d, r=r, lo=lo, hi=hi))
                else:
                    outfile.write('{t}{t}"""\n'
                                  '{t}{t}:value: {r}\n'
                                  '{t}{t}"""\n'
                                  '{t}{t}return int(self._read({a}))\n'.format(t=t, a=csr_dict[name]['Address'], r=r))

                outfile.write('\n{t}@{n}.setter\n'
                              '{t}def {n}(self, value):\n'
                              '{t}{t}"""\n'
                              '{t}{t}:value: {r}\n'
                              '{t}{t}"""\n'.format(t=t, n=name, r=r))

                if csr_dict[name]['Type'] == 'Parameter':
                    hi = csr_dict[name]['HighBit']
                    lo = csr_dict[name]['LowBit']
                    outfile.write('{t}{t}prev_value = self._read({a})\n'
                                  '{t}{t}hi = {hi}\n'
                                  '{t}{t}lo = {lo}\n'
                                  '{t}{t}mask = (((0x1 << (hi + 1)) - 1) >> lo) << lo\n'
                                  '{t}{t}value = value << lo\n'
                                  '{t}{t}masked_value = value & mask\n'
                                  '{t}{t}if masked_value != value:\n'
                                  '{t}{t}{t}raise ValueError("Value %d does not fit in the bit slice'
                                  ' [%d:%d]" % (value, hi, lo))\n'
                                  '{t}{t}self._write({a}, masked_value | (prev_value & ~mask))\n'.format(
                                    t=t, a=csr_dict[name]['Address'], lo=lo, hi=hi))
                else:
                    outfile.write('{t}{t}self._write({a}, value)\n'.format(t=t, a=csr_dict[name]['Address']))


if __name__ == '__main__':
    register_map = RegisterMap()
    register_map.parse_flat_spreadsheet("C:\\SVN\\CLI\\trunk\\Devices\\gn2554_register_map_alternative.xls",
                                        "gn2554_csr")

    # global csr creation
    global_registers = register_map.get_global_registers([0, 1, 2, 3, 'common'])

    register_map.create_csr_class("C:\\SVN\\CLI\\trunk\\Devices\\global_csr.py", global_registers, 'global_csr')

    # lane csr creation
    for lane in [0, 1, 2, 3]:
        lane_registers = register_map.get_lane_registers(lane)
        register_map.create_csr_class("C:\\SVN\\CLI\\trunk\\Devices\\lane_{}_csr.py".format(lane),
                                      lane_registers, 'lane_{}_csr'.format(lane))


