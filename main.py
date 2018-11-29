#  Author: Illin
#  Sep 2018
file_to_load = "20.lmc"

#  ---- Constants ----
instructions = {
    "HLT": "0000",     # Halt the program
    "ADD": "1",     # Add the number at the address to the accumulator
    "SUB": "2",     # Subtract the content of the address from the accumulator
    "STA": "3",     # Store the accumulator to the address
    "ACC": "4",     # Set the acuumulator to the given value
    "LDA": "5",     # Load the content from address to accumulator

    "BRA": "6",     # Branch to address
    "BRZ": "7",     # Branch if accumulator is zero
    "BRP": "8",     # Branch if accumulator is positive or zero
    "BRN": "9",     # Branch if accumulator is negitive
    "BRD": "f008",  # Branch to the location specified in the ALU

    "AND": "a",     # Binary And
    "NOT": "f00a",  # Binary Not
    "XOR": "b",     # Binary Xor
    "ORR": "c",     # Binary Or
    "LSH": "d",     # Binary Left shift
    "RSH": "e",     # Binary Right shift


    "INP": "f001",  # Take user input
    "OUT": "f002",  # Output accumulator
    "PNT": "f003",  # Print the character in the accumulator 
    "PSH": "f004",  # Push accumulator to stack
    "POP": "f005",  # Pop top of stack to accumulator
    "PEK": "f006",  # Peak top of stack to accumulator    

    "DAT": "",      # Data Storage
}

#  ---- Variables ----

acc = 0  # Accumulator
pc  = 0  # Program counter
mar = 0  # Memory address register
mdr = 0  # Memory data register
cir = 0  # Current instruction register
ram = ["0x0000"]*(16**3)
stack = []


#  ---- Code ----

#  ---- Functions ---
def split_line(text, white_space=(" ", "\t"), remove=("\n", ), length=3):
    output = []
    temp = ""
    ws = False
    for char in text:
        if char in white_space:
            if not ws:
                output.append(temp)
                temp = ""
                ws = True
        else:
            if char not in remove:
                temp += char
            ws = False
    if not ws:
        output.append(temp)
    while len(output) < length:
        output.append("")
    valid = False
    for i in output:
        if i != "":
            valid = True
    if valid:
        return output
    else:
        return [""]


# Load code from code file
# Split into [Label, Command, Value]
code = []
with open(file_to_load, "r") as file:
    for line in file:
        if len(line) > 0:
            if line[0] != "#":
                split = split_line(line)
                if len(split) > 1:
                    code.append(split)


# Generate label table
labels = {}
count = 0
for line in code:
    if line[0] != "":
        labels[line[0]] = count
    count += 1

# Equate lables and write to [Command, Value]
for c, v in enumerate(code):
    if code[c][2] in labels:
        code[c][2] = labels[code[c][2]]
    code[c] = code[c][1:]

# Convert to machine code:
for c, v in enumerate(code):
    value = ""
    if code[c][1] != "":
        value = hex(int(code[c][1]))[2:]
        while len(value) < 3:
            value = "0" + value
    code[c] = "0x" + instructions[code[c][0]] + value
    if code[c] == "0x":
        code[c] = "0x0000"
    while len(code[c]) < 6:
        code[c] = "0x0" + code[c][2:]

print(code)
# Write to ram
for c, v in enumerate(code):
    ram[c] = v


#  ---- Functions ---
def input_data():
    inp_data = ""
    valid = False
    while not valid:
        inp_data = input(">")
        try:
            inp_data = int(inp_data)
            valid = True
        except ValueError:
            print("Invalid Input")
            valid = False
    return inp_data


def output_data(o_data):
    print(o_data)


#  ---- Computer ----
running = True
while running:
    mar = pc
    pc += 1
    mdr = ram[mar]
    cir = mar
#    print("acc " + str(acc))
#    print("pc  " + str(pc))
#    print("mar " + str(mar))
#    print("mdr " + str(mdr))
#    print("------------")

    operand = int("0x" + mdr[3:], 16)
    data = int(mdr, 16)

    if data == 0:         # Hlt
        running = False

    elif mdr[2] == "1":   # Add
        acc = acc + int(ram[operand], 16)

    elif mdr[2] == "2":   # Sub
        acc = acc - int(ram[operand], 16)

    elif mdr[2] == "3":   # Sta
        ram[operand] = hex(acc)

    elif mdr[2] == "4":   # acc
        acc = operand

    elif mdr[2] == "5":   # Lda
        acc = int(ram[operand], 16)

    elif mdr[2] == "6":   # Bra
        pc = operand

    elif mdr[2] == "7":   # Brz
        if acc == 0:
            pc = operand

    elif mdr[2] == "8":   # Brp
        if acc >= 0:
            pc = operand

    elif mdr[2] == "9":   # Brn
        if acc < 0:
            pc = operand

    elif mdr[2] == "a":   # And
        acc = acc & int(ram[operand],16)
        
    elif mdr[2] == "b":   # Xor
        acc = acc ^ int(ram[operand],16)

    elif mdr[2] == "c":   # Orr
        acc = acc | int(ram[operand],16)

    elif mdr[2] == "d":   # Lsh
        acc = acc <<int(ram[operand],16)

    elif mdr[2] == "e":   # Rsh
        acc = acc >>int(ram[operand],16)

    elif mdr[2] == "f":   # Control
        if operand == 1:  # Inp
            acc = input_data()

        elif operand == 2:  # Out
            output_data(acc)
        
        elif operand == 3:  # Print
            print(chr(acc), end="", flush=True)

        elif operand == 4:  # Push
            stack.append(acc)

        elif operand == 5:  # Pop
            if len(stack) == 0:
                acc = 0
            else:
                acc = stack[len(stack)-1]
                del(stack[len(stack)-1])

        elif operand == 6:  # Peak
            if len(stack) == 0:
                acc = 0
            else:
                acc = stack[len(stack)-1]

        elif operand == 8:  # Jump to address in Accumulator
            pc = acc

        elif operand == 10:  # Not
            acc = ~acc
