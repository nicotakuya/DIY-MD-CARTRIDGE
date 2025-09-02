# MD FLASHROM WRITER for Raspberry Pi(Python)
# BY TAKUYA MATSUBARA
import os
import spidev
import time
import RPi.GPIO as GPIO

MEGA = 1024*1024
ADR1M = int(1*MEGA/8) #ADDRESS
ADR2M = int(2*MEGA/8) #ADDRESS
ADR4M = int(4*MEGA/8) #ADDRESS
ADR8M = int(8*MEGA/8) #ADDRESS

chipsize = ADR4M      #SST39SF040
romwordmax = chipsize

SAFE= 18 #GPIO NUMBER
RD  = 23 #GPIO NUMBER
ROM = 24 #GPIO NUMBER
WE  = 25 #GPIO NUMBER
CHIPSEL = ROM
ENABLE = RD

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 400000

#---
def fileselect():
    print("SELECT IMAGE FILE")
    #カレントディレクトリの一覧
    filelist = os.listdir()
    fileindex = []
    index = 0
    for file in filelist:
        ext = file[-4:].upper()
        if ext==".BIN" : # filter
            index = index+1
            print(" "+str(index)+": "+file)
            fileindex.append(index)
        else:
            fileindex.append(0)

    if index ==0:
        print("Error:File not found")
        return ""
        
    num = input("SELECT NUMBER?(1-"+str(index)+"):")
    if num=="" :
        return ""

    num = int(num)
    if num<=0 or num>index:
        return ""
    
    index = fileindex.index(num)
    print("FILE NAME:"+filelist[index])    
    return filelist[index]

#---
def verify():
    print("VERIFY ROM")
    filename = fileselect()
    if filename=="" : return

    f = open(filename, 'rb')
    bindata = f.read()
    f.close()
    bufsize = len(bindata)

    print("READ "+str(bufsize)+" BYTES("+str(int(bufsize*8/MEGA))+"M BITS)")
    print("VERIFY...")

    GPIO.output(RD,GPIO.HIGH)
    GPIO.output(ROM,GPIO.HIGH)
    GPIO.output(WE,GPIO.HIGH)
    mcp23s17setdataMODE(0) #0:INPUT/1:OUTPUT

    GPIO.output(CHIPSEL,GPIO.LOW)
    time.sleep(0.001)

    errflag = 0
    romadr = 0
    binadr = 0
    while 1:
        if binadr>=len(bindata) : break #END OF FILE
        if romadr>=romwordmax : break

        time.sleep(0.00002)
        mcp23s17setadr(romadr)
        time.sleep(0.00002)
        GPIO.output(ENABLE,GPIO.LOW)   #ENABLE
        time.sleep(0.00002)
        readdata = mcp23s17getdata()
        GPIO.output(ENABLE,GPIO.HIGH)  #ENABLE

        tmp = (bindata[binadr]<<8) + bindata[binadr+1]
        if readdata != tmp :
            errflag = errflag+1
            print("ERR"+str(errflag))
            print(" ADR="+"{:08X}".format(romadr)+" NG="+"{:04X}".format(readdata)+":OK="+"{:04X}".format(TMP))
 
        romadr = romadr+1
        binadr = binadr+2

    GPIO.output(ENABLE,GPIO.HIGH)
    GPIO.output(CHIPSEL,GPIO.HIGH)

    if errflag :
        print("NG")
    else:
        print("OK!")

#---
def romread():
    GPIO.output(RD,GPIO.HIGH)
    GPIO.output(ROM,GPIO.HIGH)
    GPIO.output(WE,GPIO.HIGH)
    mcp23s17setdataMODE(0) #0:INPUT/1:OUTPUT
    print("READ ROM 256 BYTES")
    a = input("ADDRESS(HEX)?:")
    if a=="" : a="0"
    romadr = int(a,16)
    GPIO.output(CHIPSEL,GPIO.LOW)
    time.sleep(0.001)

    work = ""
    work2 = ""
    for i in range(0x100):
        time.sleep(0.00002)
        mcp23s17setadr(romadr)
        time.sleep(0.00002)
        GPIO.output(ENABLE,GPIO.LOW) #ENABLE
        time.sleep(0.00002)
        readdata = mcp23s17getdata()
        GPIO.output(ENABLE,GPIO.HIGH) #ENABLE
        x = romadr % 8
        if x==0 :
            if work!="" :
                print(work,work2)

            work = "{:08X}".format(romadr)+":"
            work2 = "|"

        work += "{:04X}".format(readdata)
        work += " "
        work2 += code2chr(readdata >> 8)   # high
        work2 += code2chr(readdata & 0xff) # low
        romadr = romadr+1

    if work!="" :
        print(work,work2)

    GPIO.output(ENABLE,GPIO.HIGH)
    GPIO.output(CHIPSEL,GPIO.HIGH)

#---
def romwrite():
    print("WRITE IMAGE TO ROM")
    filename = fileselect()
    if filename=="" : return

    f = open(filename, 'rb')
    bindata = f.read()
    f.close()
    bufsize = len(bindata)
    print("READ "+str(bufsize)+" BYTES("+str(bufsize*8/MEGA)+"M BITS)")

    GPIO.output(WE,GPIO.HIGH)  #DISABLE
    GPIO.output(RD,GPIO.HIGH)  #DISABLE
    GPIO.output(ROM,GPIO.HIGH)  #DISABLE
    mcp23s17setdataMODE(1) #0:INPUT/1:OUTPUT

    if inputyn()=="N" : return

    startcnt = time.time()
    errflag = 0
    romadr = 0
    binadr = 0
    while 1:
        if binadr>=bufsize : break #END OF FILE
        if romadr>=romwordmax : break

        writedata = bindata[binadr] << 8          #high
        binadr = binadr+1
        writedata = writedata + bindata[binadr]   #low
        binadr = binadr+1
 
        flashwriteword(romadr,writedata)

        if (romadr & 0xff)==0 :
            work = "write adr:"
            work += "{:08X}".format(romadr)
            work += "/"+"{:08X}".format(int((bufsize/2)-1))
            work += "("+str(int(binadr*100/bufsize))+"%)"
            print(work)

        if errflag :
            return

        romadr = romadr+1

    mcp23s17setdataMODE(0) #0:INPUT/1:OUTPUT
    if errflag :
        return

    print()
    print("COMPLETE")
    endcnt = time.time()
    worktime = int((endcnt - startcnt)/60)
    print("RUNNING TIME:"+str(worktime)+" MINUTE")

#---
def flashchiperase():
    print("FLASH MEMORY CHIP ERASE")
    if inputyn()=="N" : return

    for romadr in range(0, romwordmax, chipsize):
        print("ADDRESS "+"{:08X}".format(romadr)+" - "+"{:08X}".format(romadr+chipsize-1))
        flashchiperasesub(romadr)

#---
def code2chr(chrnum):
    if chrnum>=0x20 and chrnum<=0x7f :
        return "{:c}".format(chrnum)
    else:
        return "."

#---
def flashwriteword(romadr,writedata):
    if writedata==0xffff :
        return

    chipadr = int(romadr/chipsize)*chipsize #
    GPIO.output(RD,GPIO.HIGH)  #DISABLE
    GPIO.output(WE,GPIO.HIGH)  #DISABLE
    GPIO.output(ROM,GPIO.HIGH) #DISABLE
    clkwait()
    GPIO.output(CHIPSEL,GPIO.LOW) #ENABLE

    #SST39SF040
    setadr_data(chipadr+0x5555,0xAAAA) #CYCLE1
    setweclk()
    setadr_data(chipadr+0x2AAA,0x5555) #CYCLE2
    setweclk()
    setadr_data(chipadr+0x5555,0xA0A0) #CYCLE3
    setweclk()
    setadr_data(romadr,writedata)   #CYCLE4
    setweclk()

    GPIO.output(CHIPSEL,GPIO.HIGH)  #DISABLE
    clkwait()

#---
def flashchiperasesub(romadr):
    chipadr = int(romadr/chipsize)*chipsize #
    mcp23s17setdataMODE(1) #0:INPUT/1:OUTPUT

    GPIO.output(ENABLE,GPIO.LOW) #ENABLE
    GPIO.output(WE,GPIO.HIGH)    #DISABLE
    GPIO.output(RD,GPIO.HIGH)    #DISABLE
    clkwait()
    setadr_data(chipadr+0x5555,0xAAAA) #CYCLE1
    GPIO.output(CHIPSEL,GPIO.LOW) #ENABLE
    clkwait()
    GPIO.output(ENABLE,GPIO.HIGH)
    clkwait()
    setweclk() #WE=LOW-->HIGH
    GPIO.output(CHIPSEL,GPIO.HIGH)
    setadr_data(chipadr+0x2AAA,0x5555) #CYCLE2
    GPIO.output(CHIPSEL,GPIO.LOW)
    setweclk() #WE=LOW-->HIGH
    setadr_data(chipadr+0x5555,0x8080) #CYCLE3
    setweclk() #WE=LOW-->HIGH
    setadr_data(chipadr+0x5555,0xAAAA) #CYCLE4
    setweclk() #WE=LOW-->HIGH
    setadr_data(chipadr+0x2AAA,0x5555) #CYCLE5
    setweclk() #WE=LOW-->HIGH
    setadr_data(chipadr+0x5555,0x1010) #CYCLE6
    setweclk() #WE=LOW-->HIGH

    for i in range(30):
        print(" "+str(i+1)+"/30")
        time.sleep(1)

    GPIO.output(CHIPSEL,GPIO.HIGH)  #DISABLE
    GPIO.output(ENABLE,GPIO.HIGH)
    mcp23s17setdataMODE(0) #0:INPUT/1:OUTPUT
    print("初期化完了")

#---
def setadr_data(romadr,writedata):
    mcp23s17setadr(romadr)
    mcp23s17setdata(writedata)

#---
def setweclk():
    time.sleep(0.00002)
    GPIO.output(WE,GPIO.LOW)  #ENABLE
    time.sleep(0.00002)
    GPIO.output(WE,GPIO.HIGH)  #DISABLE
    time.sleep(0.00002)

#---
def mcp23s17getdata():
    getw = mcp23s17recv(2,0x13)  # CHIP2:B
    getw = (getw << 8)
    getw += mcp23s17recv(2,0x12) # CHIP2:A
    return getw

#---
def mcp23s17setdata(DAT):
    mcp23s17send(2,0x12,(DAT & 0xFF)) #CHIP2 GPIOA かい8bit
    mcp23s17send(2,0x13,(DAT >> 8))     #CHIP2 GPIOB じょうい8bit

#---
def mcp23s17setadr(workadr):
    mcp23s17send(0,0x12,(workadr & 0xFF))       #A00-07 CHIP0:A
    mcp23s17send(0,0x13,((workadr>>8) & 0xFF))  #A08-15 CHIP0:B
    mcp23s17send(1,0x12,((workadr>>16) & 0xFF)) #A16-23 CHIP1:A

#---
def mcp23s17setdataMODE(D):   #0:INPUT/1:OUTPUT
    if D :
        mcp23s17send(2,0x00,0x00) #CHIP2 IODIRA OUTPUT
        mcp23s17send(2,0x01,0x00) #CHIP2 IODIRB OUTPUT
    else:
        mcp23s17send(2,0x00,0xFF) #CHIP2 IODIRA INPUT
        mcp23s17send(2,0x01,0xFF) #CHIP2 IODIRB INPUT

#---
def mcp23s17init():
    GPIO.setmode(GPIO.BCM)   # GPIO
    GPIO.setup(SAFE, GPIO.OUT)
    GPIO.setup(RD, GPIO.OUT)
    GPIO.setup(ROM, GPIO.OUT)
    GPIO.setup(WE, GPIO.OUT)
    GPIO.output(RD,GPIO.HIGH)
    GPIO.output(ROM,GPIO.HIGH)
    GPIO.output(WE,GPIO.HIGH)
    GPIO.output(SAFE,GPIO.LOW)
    time.sleep(0.015)
    mcp23s17send(0,0x0A,0x28)  #CHIP0 IOCON
    #  BANK/MIRROR/SEQOP    /DISSLW  /HAEN    /ODR     /INTPOL  /0
    #  0   /0     /1=disable/0=enable/1=enable/0=active/0=lowact/0

    mcp23s17send(0,0x00,0x00) #CHIP0 IODIRA OUTPUT
    mcp23s17send(0,0x01,0x00) #CHIP0 IODIRB OUTPUT

    mcp23s17send(1,0x00,0x00) #CHIP1 IODIRA OUTPUT
    mcp23s17send(1,0x01,0xFF) #CHIP1 IODIRB INPUT

    mcp23s17send(2,0x00,0xFF) #CHIP2 IODIRA INPUT
    mcp23s17send(2,0x01,0xFF) #CHIP2 IODIRB INPUT

    mcp23s17send(0,0x12,0x00) #CHIP0 GPIOA
    mcp23s17send(0,0x13,0x00) #CHIP0 GPIOB

    mcp23s17send(1,0x12,0x00) #CHIP1 GPIOA
    mcp23s17send(1,0x13,0x00) #CHIP1 GPIOB

    mcp23s17send(2,0x12,0x00) #CHIP2 GPIOA
    mcp23s17send(2,0x13,0x00) #CHIP2 GPIOB

#---
def mcp23s17send(chip,address, dat):
    spibuf = [ 0x40+(chip<<1) , address , dat ]
    spi.xfer(spibuf)
    clkwait()

#---
def mcp23s17recv(chip,address):
    spibuf = [ 0x40+(chip<<1)+1, address, 0]
    recvbuf = spi.xfer(spibuf)
    clkwait()
    return(recvbuf[2])

#---
def clkwait():
    time.sleep(0.00005)

#---
def filedump():
    print("IMAGE FILE DUMP")
    filename = fileselect()
    if filename=="" : return

    f = open(filename, 'rb')
    bindata = f.read()
    f.close()
    bufsize = len(bindata)

    print("READ "+str(bufsize)+" BYTES("+str(int(bufsize*8/MEGA))+"M BITS)")
    a  = input("ADDRESS(HEX)?:")
    if a=="" : a="0"
    romadr = int(a,16)
    work = ""
    work2 = ""
    for i in range(0x200):
        if romadr>=bufsize : break
        x = romadr % 16
        writedata = bindata[romadr]
        if x==0 :
            if work!="" :
                print(work,work2)
            work = "{:08X}".format(romadr)+":"
            work2 = "|"
        work += "{:02X}".format(writedata)
        work += " "
        work2 += code2chr(writedata)
        romadr = romadr+1

    if work!="" :
        print(work,work2)

#---
def inputyn():
    while 1:
        yn = input(" よろしいですか? [Y]/[N]:")
        yn = yn.upper()
        if yn=="Y" or yn=="":
            break

        if yn=="N" :
            break

    return yn

#---
mcp23s17init()

while 1:
    print("")
    print("---MENU")
    print("TARGET=FLASHROM("+str(int(romwordmax*8*2/MEGA))+"M bits)")
    print(" 1:READ ROM(256バイト 読み込みテスト)")
    print(" 3:ERASE FLASH MEMORY(ROMの中身を消去)")
    print(" 4:WRITE IMAGE TO ROM(ROMにイメージを書き込み)")
    print(" 5:VERIIFY(ROMを読んでイメージと比較する)")
    print(" 8:DUMP IMAGE FILE(イメージファイルを見る)")
    print(" 0:EXIT")
    cmd = input("COMMAND?:")
    if cmd=="1" : romread()
    if cmd=="3" : flashchiperase()
    if cmd=="4" : romwrite()
    if cmd=="5" : verify()
    if cmd=="8" : filedump()
    if cmd=="0" : break

print("END")
