from sys import argv, getsizeof
from math import *

# bits we are compiling to
bits = 64

# registers
REG = []
# bits that can be assigned
DB = ["db", "dw", "dd", "dq", "dt"]

# number of read-only local data
LD = 0

# number of local condition labels
LC = 0

# final SECTION rodata for read-only data
SECTION_rodata = "SECTION .rodata\n"

# final SECTION data for read / write data
SECTION_data = "SECTION .data\n"

# final SECTION text for code
SECTION_text = " SECTION .text\n"

# current label editing
LABEL = ""

# current sublabel
subLABEL = ""

# itoa
ITOA = """
section .data
    buffer  times 11 db 0
    nega db "neg",0
    posi db "pos",0
section .text
    global  ft_itoa
    extern  ft_strdup
    extern  malloc
ft_itoa:
    xor     rcx, rcx                    ;initialize counter
    xor     r9, r9                      ;set neg flag to 0
    mov     eax, edi                    ;move number in RAX for DIV instruction
    push    rbx                         ;save RBX
    mov     ebx, 10
.check_negative:
    and     edi, 0x80000000
    mov     rdi, buffer
    jz      .divide                     ;number is positive, proceed to main loop
    not     eax                         ;else
    inc     eax                         ;compute absolute value with binary complement
    inc     r9                          ;set neg flag
.divide:
    xor     edx, edx
    div     ebx
    add     edx, 48                     ;convert int to char
    push    rdx
    inc     rcx
    cmp     eax, 0
    jnz     .divide
.check_neg_flag:
    cmp     r9, 1
    jne     .buff_string
    mov     byte[rdi], '-'
.buff_string:
    pop     rdx
    mov     byte[rdi + r9], dl
    dec     rcx
    inc     r9
    cmp     rcx, 0
    jnz     .buff_string
.dup:
    mov     byte[rdi + r9], 0
    call    ft_strdup                   ;copy buffer string in memory and return pointer
    pop     rbx                         ;restore RBX
    ret
"""

def addLD(value, DB = 4):
    SECTION_rodata+=("LD{}:\n  dd {}\n".format(LD, value) if DB == 4 else "LD{}:\n  db {}\n".format(LD, value))
def addlabel(string):
    SECTION_TEXT+=LABEL
    LABEL=string+"global {}\n{}:\n".format(string, string)
def addsublabel(string):
    LABEL+=subLABEL
    LABEL=string+"  {}:\n".format(string, string)
def addinstruction(instruction):
    LABEL+=instruction+'\n'
def addsubinstruction(instruction):
    LABEL+=instruction+'\n'
def addVar(name, value, type_):
    SECTION_data+=("  {} dd {}\n".format(name, value))
    SECTION_data+=("  {}_type db {}").format(name, type_)
def addArray(name, size, values, readonly=0):
    if not readonly:
        SECTION_data+="  {}: dd"
        for i in range(size-1):
            SECTION_rodata+= "{}, ".format(values[i])
        SECTION_data+='\n'
    else:
        SECTION_rodata+="LD{}:\n".format(LD)
        LD+=1
        SECTION_rodata+="  {}: dd "
        for i in range(size-1):
            SECTION_rodata+= "{}, ".format(values[i])
        SECTION_rodata+='\n'
def read(file):
    try:
        with open(file, 'r') as f:
            c = f.read()
    except:
        print("LScc: fatal: unable to open input file `{}' No such file or directory".format(file))
        exit()
    return c


def write(file, towrite):
    with open(file, 'w') as f:
        f.write(towrite)


def search_one(string, char):
    isinstring = 0
    string = string+' '
    first = ""
    N = len(string)
    for i in range(N):
        if string[i] == '"':
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = '"'
        elif string[i] == "'":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "'"
        if string[i] == char and isinstring == 0:
            return i
    return -1


def search(string, pattern):
    isinstring = 0
    first = ""
    string = string+' '
    M = len(pattern)
    N = len(string)
    if len(pattern) == 1:
        return search_one(string, pattern)
    for i in range(N-M):
        jj = 0
        if string[i] == '"':
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = '"'
        elif string[i] == "'":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "'"
        for j in range(M):
            if string[i + j] != pattern[j]:
                break;
            jj = j
        if jj == (M-1) and isinstring == 0:
            return i
    return -1


def searchend(string, pattern):
    isinstring = 0
    first = ""
    string = string+' '
    M = len(pattern)
    N = len(string)
    if len(pattern) == 1:
        return search_one(string, pattern)
    for i in range(N-M):
        jj = 0
        if string[i] == '"':
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = '"'
        elif string[i] == "'":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "'"
        for j in range(M):
            if string[i + j] != pattern[j]:
                break;
            jj = j
        if jj == (M-1) and isinstring == 0:
            return i+M
    return -1


def searchOuttaAll(string, pattern):
    isinstring = 0
    first = ""
    string = string+' '
    M = len(pattern)
    N = len(string)
    if len(pattern) == 1:
        return search_one(string, pattern)
    for i in range(N-M):
        jj = 0
        if string[i] == '"':
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = '"'
        elif string[i] == "'":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "'"
        elif string[i] == "%":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "%"
        elif string[i] == "$":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "$"
        for j in range(M):
            if string[i + j] != pattern[j]:
                break;
            jj = j
        if jj == (M-1) and isinstring == 0:
            return i
    return -1


def getAllLines(string):
    args = [""]
    alist = 0
    isAltSix = 0
    for i in range(len(string)):
        if string[i] == '\n' and string[i-1] != '|':
            args.append("")
            alist = alist + 1
        elif string[i-1] == '|' and string[i] == '\n':
            args[alist] = args[alist][:len(args[alist])-1]
        else:
            args[alist] = args[alist] + string[i]
    return args
    

def isstring(string):
    pos = []
    tosearch = '"'
    if string.find('"') < string.find("'"):
        tosearch = "'"
    if string.find(tosearch) != -1:
        pos.append(string.find(tosearch)+1)
        string2 = string[string.find(tosearch)+1:]
        if string2.find(tosearch) != -1:
            pos.append(string2.find(tosearch)+(len(string)-len(string2)))
            return (1, pos)
        else:
            return (0, (0,0))
    else:
        return (0, (0,0))


def isvar(string):
    pos = []
    pos.append(search(string, '%')+1)
    if pos[0] != 0:
        string2 = string[pos[0]+1:]
        pos.append(search(string2, '%')+len(string)-len(string2))
        if pos[1] > pos[0]:
            return (1, pos)
        else:
            return (0, (0,0))
    else:
        return (0, (0,0))


def iscond(string):
    pos = []
    pos.append(search(string, '$')+1)
    if pos[0] != 0:
        string2 = string[pos[0]+1:]
        pos.append(search(string2, '$')+len(string)-len(string2))
        if pos[1] > pos[0]:
            return (1, pos)
        else:
            return (0, (0,0))
    else:
        return (0, (0,0))

    
def isfunc(string):
    pos = []
    if search(string, '(') != -1:
        if search(string, ')') != -1:
            return 1
        else:
            return 0
    else:
        return 0


def isfloat(string):
    chars = "0123456789."
    if string != '':
        for i in range(len(string)):
            if not string[i] in chars:
                return 0
        return 1
    return 0
    

def isint(string):
    chars = "0123456789"
    if string != '':
        for i in range(len(string)):
            if not string[i] in chars:
                return 0
        return 1
    return 0


def isbin(string):
    chars = "0b1"
    if string != '':
        for i in range(len(string)):
            if not string[i] in chars:
                return 0
        return 1
    return 0


def ishex(string):
    chars = "0x123456789ABCDEF"
    if string != '':
        for i in range(len(string)):
            if not string[i] in chars:
                return 0
        return 1
    return 0
        

def replacevar(string, var):
    i, posi = isvar(string)
    while i == 1:
        toreplace = string[posi[0]-1:posi[1]+1]
        string = string.replace(toreplace, str(var[toreplace[1:-1]]))
        i, posi = isvar(string)
    return string


def findchar(lists, char):
  find=0
  for i in range(len(lists)-1):
    if lists[i] == char:
      find=find+1
  return find


def islist(string):
    pos = []
    pos.append(search(string, '[')+1)
    if pos[0] != 0:
        string2 = string[pos[0]+1:]
        pos.append(search(string2, ']')+len(string)-len(string2))
        if pos[1] > pos[0]:
            return (1, pos)
        else:
            return (0, (0,0))
    else:
        return (0, (0,0))


def notab(string):
    isinstring = 0
    first = ""
    nstr = ""
    for i in range(len(string)):
        if string[i] == " ":
            if isinstring == 1:
                nstr = nstr + string[i]
        elif string[i] == '"':
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = '"'
            nstr = nstr + string[i]
        elif string[i] == "'":
            if isinstring == 1:
                if string[i] == first:
                    isinstring = 0
            else:
                isinstring = 1
                first = "'"
            nstr = nstr + string[i]
        else:
            nstr = nstr + string[i]
            
    return nstr


def index(script, end):
    for i in range(len(script)-1):
        if search(script[i], end) != -1:
            return i
    return -1


def getParametersF(function):
    parameters = []
    pos=1
    after = function[search(function, "(")+1:function.rfind(")")]
    afterr = after
    while pos:
        if search(after, ",") != -1:
            afterr = after[:search(after, ",")+1]
        else:
            afterr = after
        s = isvar(afterr)
        if s[0]:
            parameters.append(afterr[s[1][0]:s[1][1]])
        else:
            pos = 0
        if search(after, ",") == -1:
            after = after[:-1]
        else:
            after = after[search(after, ",")+1:]
    return parameters


def scanCondType(after):
    if search(after, "==") != -1:
        return "=="
    elif search(after, ">") != -1:
        return ">="
    elif search(after, "<") != -1:
        return "<"
    elif search(after, "!=") != -1:
        return "!="
    elif search(after, "<=") != -1:
        return "<="
    elif search(after, ">=") != -1:
        return ">="
    return -1


def scankeyType(after):
    if searchOuttaAll(after, "int") != -1:
        return "int"
    elif searchOuttaAll(after, "str") != -1:
        return "str"
    elif searchOuttaAll(after, "float") != -1:
        return "float"
    elif searchOuttaAll(after, "bin") != -1:
        return "bin"
    elif searchOuttaAll(after, "hex") != -1:
        return "hex"
    return -1


def scanOperatorEqual(after):
    if search(after, "**=") != -1:
        return "**="
    elif search(after, "*=") != -1:
        return "*="
    elif search(after, "+=") != -1:
        return "+="
    elif search(after, "-=") != -1:
        return "-="
    elif search(after, "/=") != -1:
        return "/="
    elif search(after, "%=") != -1 and isvar(after) == -1:
        return "%="
    elif search(after, "^=") != -1:
        return "^="
    elif search(after, "->") != -1:
        return "->"
    elif search(after, "=") != -1:
        return "="
    return -1


def scanOperator(after):
    if search(after, "**") != -1:
        return "**"
    elif search(after, "*") != -1:
        return "*"
    elif search(after, "+") != -1:
        return "+"
    elif search(after, "-") != -1:
        return "-"
    elif search(after, "/") != -1:
        return "/"
    elif search(after, "^") != -1:
        return "^"
    elif search(after, "%") != -1 and isvar(after) == -1:
        return "%"
    return -1


def ismath(string):
    if scanOperator(string)!=-1:
        return 1
    else:
        return 0

    
class ls():
    def __init__(self, script):
        global SECTION_rodata
        self.script = []
        self.functions = {}
        self.condition = {}
        self.default_function = {}
        # defining default functions
        self.default_function[""] = -1
        self.default_function["print(%any%)"] = 0
        self.default_function["os.file.write(%file%, %string%)"] = 1
        self.default_function["os.file.read(%file%)"] = 2
        self.default_function["write(%file%, %string%)"] = 1
        self.default_function["read(%file%)"] = 2
        self.default_function["input(%string%)"] = 3
        self.default_function["return(%any%)"] = 4
        self.default_function["len(%list%)"] = 5
        self.default_function["goto(%name%)"] = 6
        self.default_function["label(%name%)"] = 7
        self.default_function["sin(%float%)"] = 8
        self.default_function["cos(%float%)"] = 9
        self.default_function["tan(%float%)"] = 10
        # defining default vars
        SECTION_rodata+="pi:\n  dd {}\n".format(pi)
        for i in getAllLines(script):
            if search(i, '#') != -1:
                self.script.append(i[:search(i, '#')])
            else:
                comma = search(i, ';')
                if comma != -1:
                    self.script.append(i[:comma])
                    self.script.append(i[comma+1:])
                else:
                    self.script.append(i)


    def parse(self, script):
        for l in range(len(self.script)-1):
            subscript = self.script[l]
            if search(subscript, "def") != -1 and search(subscript, ":") != -1:
                self.functions[subscript[4:search(subscript, ':')]] = l


    def typescan(self, after, line, test = 0):
        after = notab(after)
        if test == 0:
            if islist(after)[0] and (isvar(after)[1][0] > islist(after)[1][0] or isvar(after)[0] == 0):
                return self.getlist(after, line)
            elif isfunc(after):
                return self.exec(after, line)
            elif isvar(after)[0]:
                if isvar(after)[1][0] < islist(after)[1][0]:
                    index = getlist(after, line)[0]
                    s = isvar(after)
                    return after[s[1][0]:s[1][1]][{}]
                s = isvar(after)
                return after[s[1][0]:s[1][1]]
            else:
                return after
            return -1
        else:
            if islist(after)[0] and (isvar(after)[1][0] > islist(after)[1][0] or isvar(after)[0] == 0):
                return "l"
            elif isfunc(after):
                return "f"
            elif isstring(after)[0]:
                return "s"
            elif isint(after):
                return "i"
            elif isfloat(after):
                return "f"
            elif isbin(after):
                return "b"
            elif ishex(after):
                return "h"
            elif ismath(after) and scanOperator(after) != -1:
                return "f"
            elif isvar(after)[0]:
                return "v"
            return -1


    def tokeytype(self, keytype, after, line):
        if keytype == -1:
            return self.typescan(after, line)
        elif keytype == "int":
            return int(self.typescan(after, line))
        elif keytype == "str":
            return str(self.typescan(after, line))
        elif keytype == "float":
            return float(self.typescan(after, line))
        elif keytype == "bin":
            return bin(self.typescan(after, line))
        elif keytype == "hex":
            return hex(self.typescan(after, line))
        else:
            return self.typescan(after, line)
        
            
    def scanVarI(self, l, line):
        pos = isvar(l)
        tosearch = scanOperatorEqual(l)
        posint = search(l, tosearch)
        after = l[posint+len(tosearch):]
        posi = pos[1]
        keytype = scankeyType(l)
        if tosearch == "->":
            self.scanPointI(l, line)
            return
        print(l[posi[0]:posi[1]])
        if posint > islist(l)[1][0] and islist(l)[0] != 0:
            index = self.getlist(l, line)[0]
            if tosearch == "**=":
                addinstruction("mov {}, {}".format(REG[1], "'a'"))
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] ** self.tokeytype(keytype, after, line)
            elif tosearch == "*=":
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] * self.tokeytype(keytype, after, line)
            elif tosearch == "+=":
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] + self.tokeytype(keytype, after, line)
            elif tosearch == "-=":
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] - self.tokeytype(keytype, after, line)
            elif tosearch == "/=":
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] / self.tokeytype(keytype, after, line)
            elif tosearch == "%=":
                self.var[l[posi[0]:posi[1]]][index] = self.var[l[posi[0]:posi[1]]][index] % self.tokeytype(keytype, after, line)
            elif tosearch == "^=":
                self.var[l[posi[0]:posi[1]]][index] = self.tokeytype(keytype, after, line) ^ semf.tokeytype(keytype, after, line)
            elif tosearch == "=":
                self.var[l[posi[0]:posi[1]]][index] = self.tokeytype(keytype, after, line)
        else:
            if tosearch == "**=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] ** self.tokeytype(keytype, after, line)
            elif tosearch == "*=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] * self.tokeytype(keytype, after, line)
            elif tosearch == "+=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] + self.tokeytype(keytype, after, line)
            elif tosearch == "-=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] - self.tokeytype(keytype, after, line)
            elif tosearch == "/=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] / self.tokeytype(keytype, after, line)
            elif tosearch == "%=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] % self.tokeytype(keytype, after, line)
            elif tosearch == "^=":
                self.var[l[posi[0]:posi[1]]] = self.var[l[posi[0]:posi[1]]] ^ self.tokeytype(keytype, after, line)
            elif tosearch == "=":
                
                self.var[l[posi[0]:posi[1]]] = self.tokeytype(keytype, after, line)


    def getParameters(self, function, line):
        parameters = []
        pos=1
        l = function
        after = l[search(l, "(")+1:l.rfind(")")]
        if l.rfind(')') == -1:
            after+=')'
        afterr = after
        while pos:
            if search(after, ",") != -1:
                afterr = after[:search(after, ",")+1]
            else:
                afterr = after
                
            if self.typescan(afterr, line, 1) != -1:
                parameters.append(self.tokeytype(-1, afterr, line))
            else:
                pos = 0
                
            if search(after, ",") == -1:
                after = after[:-1]
            else:
                after = after[search(after, ",")+1:]
        return parameters


    def getlist(self, string, line):
        parameters = []
        pos=1
        l = string
        after = l[search(l, "[")+1:l.rfind("]")]
        afterr = after
        while pos:
            if search(after, ",") != -1:
                afterr = after[:search(after, ",")]
            else:
                afterr = after
            if self.typescan(afterr, line) != -1:
                parameters.append(self.tokeytype(-1, afterr, line))
            else:
                pos = 0
                
            if search(after, ",") == -1:
                after = after[:-1]
            else:
                after = after[search(after, ",")+1:]
        return parameters
    

    def getdict(self, string, line):
        parameters = []
        pos=1
        l = string
        after = l[search(l, "[")+1:l.rfind("]")]
        afterr = after
        while pos:
            if search(after, ",") != -1:
                afterr = after[:search(after, ",")+1]
            else:
                afterr = after
                
            if self.typescan(afterr, line) != -1:
                parameters.append(self.tokeytype(-1, afterr, line))
            else:
                pos = 0
                
            if search(after, ",") == -1:
                after = after[:-1]
            else:
                after = after[search(after, ",")+1:]
        return parameters


    def scanCondI(self, l):
        pos = iscond(l)
        after = l[search(l, "=")+1:]
        posi = pos[1]
        self.condition[l[posi[0]:posi[1]]] = notab(after)


    def scanPointI(self, l, line):
        before = l[:search(l, "->")]
        after = notab(l[searchend(l, "->"):])
        pos = isvar(after)[1]
        after = after[pos[0]:pos[1]]
        if self.typescan(before, line, 1) == "var":
            self.var[after] = '&'+before
        else:
            self.scanVarI(self.var[after]+'='+before, line)
        return

            
    def condI(self, l, line):
        pos = iscond(l)
        iselse = 0
        if pos[0]:
            posi = pos[1]
            f = notab(l[posi[1]+1:])
            if search(l, '!') == posi[0]:
                iselse = 1
                c = self.condition[l[posi[0]+1:posi[1]]]
            else:
                c = self.condition[l[posi[0]:posi[1]]]
            after = self.tokeytype(-1, c[search(c, "=")+1:], line)
            before = self.tokeytype(-1, c[:search(c, "=")], line)
            if search(c, "==") != -1:
                if before == after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            elif search(c, ">") != -1:
                if before > after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            elif search(c, "<") != -1:
                if before < after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            elif search(c, "!=") != -1:
                if before != after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            elif search(c, "<=") != -1:
                if before <= after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            elif search(c, ">=") != -1:
                if before >= after:
                    if iselse == 0:
                        return self.exec_(f, line, [], f, one=l)
                else:
                    if iselse == 1:
                        return self.exec_(f, line, [], f, one=l)
            

    def exec_(self, i, line, parameters, function, end = "end def", one = 0):
        toreturn = None
        if one == 0:
            j=0
            func = self.functions[i]
            line = func
            script = self.script[func:]
            parametersF = getParametersF(script[0])
            script = script[1:index(script, end)]
            if not '...args' in parametersF:
                if len(parameters) > len(parametersF):
                    print("Warning: too many parameters for function `{}', at line {}".format(function, line))
            else:
                print("param", parameters, i)
                parametersPP = parameters[:len(parametersF)+1]
                print("paramP", parametersPP, i)
                parametersP = parameters[len(parametersPP):]
                print("paramPP", parametersP, i)
                parameters = parametersPP
                parameters.append(parametersP)
                print("param", parameters, i)
            if len(parameters) < len(parametersF):
                print("Error: not enough parameters for function `{}', at line {}".format(function, line))
                exit()
            for j in range(len(parametersF)):
                self.var[parametersF[j]] = parameters[j]
            while j != len(script):
                line2 = line + j
                i = script[j]
                if iscond(i)[0] == 0 and isvar(i) != -1 and scanOperatorEqual(i) != -1:
                    self.scanVarI(i, line2)
                elif iscond(i)[0] == 1 and scanCondType(i) != -1:
                    self.scanCondI(i)
                elif iscond(i)[0] == 1:
                    toreturn = self.condI(i, line2)
                else:
                    toreturn = self.exec(i, line2)
                if type(toreturn) == type([1, 1]):
                    if toreturn[0] == "__Python__.__ls__.__sys__.__goto__":
                        j = toreturn[1]-line
                        toreturn = None
                else:
                    j += 1
            return toreturn
        else:
            line2 = line
            if iscond(i)[0] == 0 and isvar(i) != -1 and scanOperatorEqual(i) != -1:
                self.scanVarI(i, line)
            elif iscond(i)[0] == 1 and scanCondType(i) != -1:
                self.scanCondI(i)
            elif iscond(i)[0] == 1:
                toreturn = self.condI(i, line2)
            else:
                toreturn = self.exec(i, line2)
        return toreturn
            
              
    def compile(self, function, line):
        func = ""
        function = notab(function)
        toreturn = None
        parameters = self.getParameters(function, line)
        for i in self.functions:
            nf = i[:search(i, "(")]+'()'
            tcf = function[:search(function, "(")]+'()'
            if nf == tcf:
                func = i
                self.exec_(i, line, parameters, function)
                break
        for i in self.default_function:
            nf = i[:search(i, "(")+1]+i[-1:]
            tcf = function[:search(function, "(")+1]+function[-1:]
            if nf == tcf:
                parametersF = getParametersF(i)
                if len(parameters) < len(parametersF):
                    print("Error: not enough parameters for function `{}', at line {}".format(function, line+1))
                    return None
                func = i
                func = self.default_function[func]
                if func == 0:
                    continue
                elif func == 1:
                    type_ = typescan(str(parameters[0]), 1)
                    addinstruction('; printing {}'.format(parameters[0]))
                    if type_ != "v":
                        addLD(len(str(parameters[0])))
                        addLD('"'+str(parameters[0])+'"')
                        addinstruction('mov {}, 1'.format(REG[0]))
                        addinstruction('mov {}, 1'.format(REG[5]))
                        addinstruction('mov {}, {}'.format(REG[4], str(LD-1)))
                        addinstruction('mov {}, {}'.format(REG[3], str(LD-2)))
                        addinstruction('syscall')
                    else:
                        # compare if the variable type is string or not
                        var_ = str(parameters[0])
                        addinstruction("mov {}, {}_type".format(REG[0], var_))
                        addinstruction("test {}, 's'".format(REG[0]))
                        addinstruction("jz {}_{}_string".format(var_, line))
                        # integer
                        addinstruction("test {}, 'i'".format(REG[0]))
                        addinstruction("jz {}_{}_int".format(var_, line))
                        # float
                        addinstruction("test {}, 'f'".format(REG[0]))
                        addinstruction("jz {}_{}_float".format(var_, line))
                        # binary
                        addinstruction("test {}, 's'".format(REG[0]))
                        addinstruction("jz {}_{}_string".format(var_, line))
                        # hexadecimal
                        addinstruction("test {}, 's'".format(REG[0]))
                        addinstruction("jz {}_{}_string".format(var_, line))
                        # list
                        addinstruction("test {}, 's'".format(REG[0]))
                        addinstruction("jz {}_{}_list".format(var_, line))
                        # add thoses labels
                        addsublabel("{}_{}_string".format(var_, line))
                        addsubinstruction('mov {}, 1'.format(REG[0]))
                        addsubinstruction('mov {}, 1'.format(REG[5]))
                        addsubinstruction('mov {}, {}'.format(REG[4], str(LD-1)))
                        addsubinstruction('mov {}, {}'.format(REG[3], str(LD-2)))
                        addsubinstruction('syscall')
                        
                elif func == 2:
                    toreturn = read(parameters[0])
                elif func == 3:
                    addbss("in_{}".format(line), parameters[1])
                    addinstruction("mov {}, 0".format(REG[0]))
                    addinstruction("mov {}, 0".format(REG[5]))
                    addinstruction("mov {}, in_{}".format(REG[4], line))
                    addinstruction("mov {}, {}".format(REG[3], parameters[0]))
                    addinstruction("syscall")
                elif func == 4:
                    addinstruction("mow r15, {}").format(parameters[0])
                    addinstruction("ret")
                elif func == 5:
                    toreturn = len(parameters[0])
                elif func == 6:
                    addinstruction("call {}".format(parameters[0]))
                elif func == 7:
                    addinstruction("  {}:".format(parameters[0]))
                elif func == 8:
                    toreturn = sin(parameters[0])
                elif func == 9:
                    toreturn = cos(parameters[0])
                elif func == 10:
                    toreturn = tan(parameters[0])
        if func == "":
            print("LScc : Error, function not found `{}' at line {}".format(function, line))
            return None
        return toreturn
    

def main():
    global bits, REG
    if (len(argv) > 1):
        if "-i" in argv:
            file = argv[argv.index("-i")+1]
        else :
            print("LScc: fatal: no input file specified")
            exit()
        outfile = ("object.o" if not "-o" in argv else argv[argv.index("-o")+1])
        Fformat = ("obj" if not "-f" in argv else argv[argv.index("-f")+1])
        bits = ("64" if not "-b" in argv else argv[argv.index("-b")+1])
        if bits == "64":
            REG = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "xmm0", "xmm1", "xmm2", "xmm3"]
        elif bits == "32":
            REG = ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "r8d", "r9d", "r10d", "r11d", "r12d", "r13d", "r14d", "r15d"]
        elif bits == "16":
            REG = ["ax", "bx", "cx", "dx", "si", "di", "bp", "sp", "r8w", "r9w", "r10w", "r11w", "r12w", "r13w", "r14w", "r15w"]
        else:
            REG = ["al", "bl", "cl", "dl", "sil", "dil", "bpl", "spl", "r8b", "r9b", "r10b", "r11b", "r12b", "r13b", "r14b", "r15b"]
        save = (1 if "-s" in argv else 0)
        n = (1 if "-n" in argv else 0)
        reader = ls(read(file))
        reader.parse(read(file))
        for i in reader.functions:
            if "start" in i:
                reader.compile("start()", reader.functions[i])
            else:
                print(i)
        write("__CPPFILE__.cpp", fileC)
    else:
        print("""LScc: fatal: no input file specified
Usage: LScc [options...]

Options:

         -i    input file
         -o    output file
         -f    format [elf32, elf64, elfx32, obj, win32, win64, ieee, macho32, macho64] default: obj         
         -b    bits [64, 32, 16, 8] default: 64
         -n    no args
         -s    keep asm file""")
    

main()
