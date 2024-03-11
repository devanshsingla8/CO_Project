import sys


if len(sys.argv) != 3:
    print("Usage: python process_data.py input_file output_file")
    sys.exit(1)



def twos_comp(imm):
    n = int(imm)
    if n < 0:
        decimalabs = abs(n)
        
        bina = '0' + bin(decimalabs)[2:]
        
        inverted_bina = ''.join(['1' if bit == '0' else '0' for bit in bina])
        
        twocomplement = bin(int(inverted_bina, base=2) + 1)[2:]
        
        return str(twocomplement)
    else:
        return '0' + str(bin(n)[2:])

def hex_to_binary(n):
    hextobin = {'0':'0000','1':'0001','2':'0010','3':'0011','4':'0100','5':'0101','6':'0110','7':'0111','8':'1000','9':'1001','A':'1010','B':'1011','C':'1100','D':'1101','E':'1110','F':'1111'}
    n=''.join([hextobin[i] for i in n])
    return n
 


def signext(imm):
    if imm[0:2] == '0x':
        
        imm = hex_to_binary(imm[2:])
    
    else:
        
        imm = twos_comp(imm)
    
    if len(imm) > 32:
        
        return 'Error'
    
    signbit = imm[0]
    
    i = (32 - len(imm)) * signbit
    
    imm = i + imm
    
    return imm



def rconvert(parts, instruction):
    
    opcode = {'add': ['0000000', '000', '0110011'], 'sub': ['0100000', '000', '0110011'], 'sll': ['0000000', '001', '0110011'], 'slt': ['0000000', '010', '0110011'], 'sltu': ['0000000', '011', '0110011'], 'xor': ['0000000', '100', '0110011'], 'srl': ['0000000', '101', '0110011'], 'or': ['0000000', '110', '0110011'], 'and': ['0000000', '111', '0110011'], 'mul': ['0000001', '000', '0110011']}
    
    rd = parts[1]
    
    rs1 = parts[2]
    
    rs2 = parts[3]
    
    lineencode = opcode[instruction][0] + dictregister[rs2] + dictregister[rs1] + opcode[instruction][1] + dictregister[rd] + opcode[instruction][2]
    
    return lineencode + '\n'

def iconvert(parts,instruction):
    
    opcode={'lw':['010','0000011'],'addi':['000','0010011'],'sltiu':['011','0010011'],'jalr':['000','1100111']}
    
    if instruction=='lw':
    
        rd=parts[1]
    
        imm=signext(parts[2])
    
        rs1=parts[3]
    
        line_encoded=imm[32-11-1:]+dictregister[rs1]+opcode[instruction][0]+dictregister[rd]+opcode[instruction][1] 
    
    else:
    
        rd=parts[1]
    
        imm=signext(parts[3])
    
        rs=parts[2]
    
        line_encoded=imm[32-11-1:]+dictregister[rs]+opcode[instruction][0]+dictregister[rd]+opcode[instruction][1]
    
    return line_encoded+'\n'

def uconvert(parts,instruction):
    
    opcode={'lui':'0110111','auipc':'0010111'}
    
    rd=parts[1]
    
    imm=signext(parts[2])
    
    l_encoded=imm[32-31-1:32-12]+dictregister[rd]+opcode[instruction]
    
    return l_encoded+'\n'




def bconvert(parts,instruction,line_num):
    
    opcode={'beq':['000','1100011'],'bne':['001','1100011'],'blt':['100','1100011'],'bge':['101','1100011'],'bltu':['110','1100011'],'bgeu':['111','1100011']}
    
    if(parts[3].isdigit() or (parts[3][0]=='-' and parts[3][1:].isdigit())):
    
        rs1=parts[1]
    
        rs2=parts[2]
    
        imm=signext(parts[3])
    
        line_encoded=(imm[32-12-1]+imm[32-10-1:32-5])+dictregister[rs2]+dictregister[rs1]+opcode[instruction][0]+(imm[32-4-1:32-1]+imm[32-11-1])+opcode[instruction][1]
    
        return line_encoded+'\n'
    
    else:
    
        rs1=parts[1]
    
        rs2=parts[2]
    
        imm=signext(str((line_num-dict_label[parts[3]])*4))
    
        line_encoded=(imm[32-12-1]+imm[32-10-1:32-5])+dictregister[rs2]+dictregister[rs1]+opcode[instruction][0]+(imm[32-4-1:32-1]+imm[32-11-1])+opcode[instruction][1] 
    
        return line_encoded+'\n'



def jconvert(parts,instruction,line_num):#[instruction,rd,imm]
    
    opcode={'jal':'1101111'}
    
    if(parts[2].isdigit() or (parts[2][0]=='-' and parts[2][1:].isdigit())): #[1:] because there can be a - sign in start
    
        rd=parts[1]
    
        imm=signext(parts[2])
    
        l_encoded=(imm[32-20-1]+imm[32-10-1:32-1]+imm[32-11-1]+imm[32-19-1:32-12])+dictregister[rd]+opcode[instruction]
    
        return l_encoded+'\n'
    
    else:
    
        rd=parts[1]
    
        imm=signext(str((line_num-dict_label[parts[2]])*4))
    
        l_encoded=(imm[32-20-1]+imm[32-10-1:32-1]+imm[32-11-1]+imm[32-19-1:32-12])+dictregister[rd]+opcode[instruction]
    
        return l_encoded+'\n'


def sconvert(parts,instruction):
    
    opcode={'sw':['010','0100011']}
    
    imm=signext(parts[2])
    
    rs2=parts[1]
    
    rs1=parts[3]
    
    line_encoded=imm[32-11-1:32-5]+dictregister[rs2]+dictregister[rs1]+opcode[instruction][0]+imm[32-4-1:]+opcode[instruction][1] 
    
    return line_encoded+'\n'


# def bonus_conversion(line,instruction):
#     return

with open('C://Users//singl//OneDrive//Desktop//co_proj.txt','r') as f:
    
    l_code_lines=[i.rstrip('\n') for i in f.readlines()]

import re



input_file_name = sys.argv[1]
output_file_name = sys.argv[2]


with open(input_file_name, 'r') as input_file:
    
    l_code_lines=[i.rstrip('\n') for i in input_file.readlines()]


#l_code_lines = [i.rstrip('\n') for i in f.readlines()]



l_instructions = ['add', 'sub', 'slt', 'sltu', 'xor', 'sll', 'srl', 'or', 'and', 'lw', 'addi', 'sltiu', 'jalr', 'sw', 'beq', 'bne', 'bge', 'bgeu', 'blt', 'bltu', 'auipc', 'lui', 'jal', 'mul', 'rst', 'halt', 'rvrs']
l_base_instructions_R = ['add', 'sub', 'slt', 'sltu', 'xor', 'sll', 'srl', 'or', 'and']
l_base_instructions_I = ['lw', 'addi', 'sltiu', 'jalr']
l_base_instructions_S = ['sw']
l_base_instructions_B = ['beq', 'bne', 'bge', 'bgeu', 'blt', 'bltu']
l_base_instructions_U = ['auipc', 'lui']
l_base_instructions_J = ['jal']
l_base_instructions_bonus = ['mul', 'rst', 'halt', 'rvrs']
dictregister = {"zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100", "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "fp": "01000", "s1": "01001", "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110", "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011", "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"}

machine_code = []
dict_label = {}

for i in range(len(l_code_lines)):
    l_first = l_code_lines[i].lstrip(' ').split(' ')[0]
    if l_first[len(l_first) - 1] == ':':
        dict_label[l_first.replace(':', '')] = i + 1

for i in range(len(l_code_lines)):
    parts = re.split(r'[,()\s]+', l_code_lines[i])
    while parts and parts[0] not in l_instructions: 
        parts.pop(0)
    if parts:
        if parts[0] in l_base_instructions_R:
            machine_code.append(rconvert(parts, parts[0]))
        elif parts[0] in l_base_instructions_I:
            machine_code.append(iconvert(parts, parts[0]))
        elif parts[0] in l_base_instructions_S:
            machine_code.append(sconvert(parts, parts[0]))
        elif parts[0] in l_base_instructions_B:
            machine_code.append(bconvert(parts, parts[0], i + 1))
        elif parts[0] in l_base_instructions_U:
            machine_code.append(uconvert(parts, parts[0]))
        elif parts[0] in l_base_instructions_J:
            machine_code.append(jconvert(parts, parts[0], i + 1))
        # elif parts[0] in l_base_instructions_bonus: str_machine_code+=bonus_conversion(i,parts[0])
        else:
            continue
    else:
        print(f"Skipping empty line or invalid instruction: {l_code_lines[i]}")
if machine_code:  
    machine_code[-1] = machine_code[-1].replace('\n', '')


# l_machine_code[-1] = l_machine_code[-1].replace('\n', '')  



with open('C://Users//singl//OneDrive//Desktop//co_proj.txt', 'w') as f:
    for i in machine_code:
        f.write(i)


l_instructions=['add','sub','slt','sltu','xor','sll','srl','or','and','lw','addi','sltiu','jalr','sw','beq','bne','bge','bgeu','blt','bltu','auipc','lui','jal','mul','rst','halt','rvrs']
l_base_instructions_R=['add','sub','slt','sltu','xor','sll','srl','or','and']
l_base_instructions_I=['lw','addi','sltiu','jalr']
l_base_instructions_S=['sw']
l_base_instructions_B=['beq','bne','bge','bgeu','blt','bltu']
l_base_instructions_U=['auipc','lui']
l_base_instructions_J=['jal']
l_base_instructions_bonus=['mul','rst','halt','rvrs']
dict_register = {"zero": "00000","ra": "00001","sp": "00010","gp": "00011","tp": "00100","t0": "00101","t1": "00110","t2": "00111","s0": "01000","fp": "01000","s1": "01001","a0": "01010","a1": "01011","a2": "01100","a3": "01101","a4": "01110","a5": "01111","a6": "10000","a7": "10001","s2": "10010","s3": "10011","s4": "10100","s5": "10101","s6": "10110","s7": "10111","s8": "11000","s9": "11001","s10": "11010","s11": "11011","t3": "11100","t4": "11101","t5": "11110","t6": "11111"}

l_machine_code=[]
dict_label={}

for i in range(len(l_code_lines)):

    l_first=l_code_lines[i].lstrip(' ').split(' ')[0]
    
    if l_first[len(l_first)-1]==':': 
        dict_label[l_first.replace(':','')]=i+1

for i in range(len(l_code_lines)):
    parts=re.split(r'[,()\s]+',l_code_lines[i])


    while(parts[0] not in l_instructions or len(parts)==0): 
        parts.pop(0)
    
    
    if len(parts)==0: 
        continue
    if parts[0] in l_base_instructions_R: 
        l_machine_code.append(rconvert(parts,parts[0]))
    elif parts[0] in l_base_instructions_I: 
        l_machine_code.append(iconvert(parts,parts[0]))
    elif parts[0] in l_base_instructions_S: 
        l_machine_code.append(sconvert(parts,parts[0]))
    elif parts[0] in l_base_instructions_B: 
        l_machine_code.append(bconvert(parts,parts[0],i+1))
    elif parts[0] in l_base_instructions_U: 
        l_machine_code.append(uconvert(parts,parts[0]))
    elif parts[0] in l_base_instructions_J: 
        l_machine_code.append(jconvert(parts,parts[0],i+1))
    # elif parts[0] in l_base_instructions_bonus: 
        #str_machine_code+=bonus_conversion(i,parts[0])
    else: 
        continue




if l_machine_code:
    l_machine_code[len(l_machine_code)-1]=l_machine_code[len(l_machine_code)-1].replace('\n','') 







with open(output_file_name, 'w') as output_file:

    for i in l_machine_code:
        output_file.write(i)