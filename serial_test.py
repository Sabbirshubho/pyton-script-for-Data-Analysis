import struct

import time
import serial


#serial interface timeout
ser_timeout = 1
ser = 0;
# ID
k_ID_DEFAULT = 0xFFFF
k_ID_0 = 0 # demo test
k_ID_1 = 1 # config input
k_ID_2 = 2 # config output
k_ID_3 = 3 # set high
k_ID_4 = 4 # set low
k_ID_5 = 5 # get value

# commands
k_CMD_get_test_case_info = 0x1
k_CMD_exe_test = 0x2
k_CMD_get_test_parameter_info = 0x5

#-----------------------------------------------------------------------
#   open:
#   serial interface
#-----------------------------------------------------------------------
def open(host_com):
  global ser, ser_timeout
  ser = serial.Serial(host_com, 57600, timeout=ser_timeout)  # open serial port
  print(ser.name)         # check which port was really used
  res = 1
  return res
#-----------------------------------------------------------------------
#   close:
#   serial interface
#-----------------------------------------------------------------------
def close():
  global ser
  ser.close()
  res = 1
  time.sleep(1)  
  return res

#-----------------------------------------------------------------------
#   read:
#   serial interface
#   return:
#         0 - no data
#         1 - data received
#-----------------------------------------------------------------------
def read():
  global ser
  crc = 0;
  res = ser.read(100)     # read up to one hundred bytes
  if(len(res) == 0):
    #print '-no response-'
    return 0
  ret_string = res  
  while (len(res)):
    char = struct.unpack('<B',res[0:1])
    res = res[1:]
    print("%02x " % char),
    crc = crc + int(char[0])
  print(" crc:%02x," % (crc & 0xFF))  
  # get tcep message 
  if(crc & 0xFF)==0:
    id, cmd, status   = struct.unpack('<HBB', ret_string[0:4])
    length, data = struct.unpack('<HB', ret_string[4:7])  

    #######################################################
    # id = general command
    #######################################################
    if id==0xFFFF:
      #-----------------------  
      #bootup msg     
      if cmd == 0xF:
        print ('bootup msg')
      #-----------------------  
      #get test case info
      if cmd == 0x81:
        print ('get test case info resp'),
        if status == 0:
          print (' ok '),
          plength, major, minor = struct.unpack('<HBB', ret_string[7:11])
          print( 'v%d.%d'% (major, minor))
        else:
          print (' error')
      #-----------------------  
      #restart system response  
      if cmd == 0x84:
        print ('restart system resp'),
        if status == 0:
          print (' ok')
        else:
          print (' error')
        
    else:
      #######################################################
      # id = certain test case number
      #######################################################
      print( 'test %d, '% id),
      #-----------------------  
      #get test case info
      if cmd == 0x81:
        print ('get test case info resp'),
        if status == 0:
          print (' ok '),
          plength, major, minor = struct.unpack('<HBB', ret_string[7:11])
          print ('v%d.%d'% (major, minor))
        else:
          print (' error' )     
      #-----------------------  
      # exe test
      if cmd == 0x82:
        print ('test resp'),
        if status == 0:
          print( ' ok ')
          if id==0x5:   # test 5: response of get value
            pvalue = struct.unpack('I', ret_string[11:15])
            print ('get value 0x%x ' % pvalue)
        else:
          print( ' error: '), 
          perror = ret_string[11:]
          print (perror)
      #-----------------------  
      #get test parameter info
      if cmd == 0x85:
        print( 'get test parameter info resp'),
        if status == 0:
          print( ' ok. '),
          ptype, pflags  = struct.unpack('BB', ret_string[7:9])
          print ('type:%x, flags:%x '% (ptype, pflags)),
          pname = ret_string[8:]
          print (pname)
        else:
          print (' error')      
    #print (id, cmd, status, length, data)
  return 1 
  
#-----------------------------------------------------------------------
#   write:
#   serial interface
#   parameter:
#          id, cmd, status, length, data
#-----------------------------------------------------------------------
def write(id, cmd, status, length, data):
  global ser
  crc = 0;
  header   = struct.pack('<HBB', id, cmd, status)
  if length:
    if type(data)==str:
      #string 
      length = length +1 # zero terminated string      
      msg_data = struct.pack('<H%ds'% (length,), length, data)
    else:
      #byte or more
      if length==1:
        msg_data = struct.pack('<HB', length, data)
      if length==4:
        msg_data = struct.pack('<HL', length, data)
  else:
    msg_data = struct.pack('<H', length)
  # crc calc
  msg = header + msg_data
  while (len(msg)):
    char = struct.unpack('<B',msg[0:1])
    print( char) 
    msg = msg[1:]
    crc = crc + int(char[0])
  print ((-crc) & 0xFF)
  crc = struct.pack('<B',((-crc) & 0xFF))
  #write whole msg now
  ser.write(header + msg_data + crc)
  return 
  
##################################################################
# main 
##################################################################
print (' ')
print ('USB-to-CAN V2 production test test')
open("COM6")
print ('wait for bootup message ...')
# get bootup msg
while (read()==0):
  print ('.'),

#print ' '  
#print 'test 1, config input'
#pdata = 0x0000
#write(k_ID_1, k_CMD_exe_test, 0x00, 4, pdata) #get test parameter info, input parameter
#time.sleep(1)
#if(read()==0):
#  print '-no response-'

#print ' '  
#print 'test 1, config input'
#pdata = 0x0001
#write(k_ID_1, k_CMD_exe_test, 0x00, 4, pdata) 
#time.sleep(1)
#if(read()==0):
#  print '-no response-'

print (' '  )
print( 'test 2, config output')
pdata = 0x003F
write(k_ID_2, k_CMD_exe_test, 0x00, 4, pdata) 
time.sleep(0.1)
if(read()==0):
  print ('-no response-')

print (' '  )
print ('test 3, set high')
pdata = 0x003F
write(k_ID_3, k_CMD_exe_test, 0x00, 4, pdata) 
time.sleep(0.1)
if(read()==0):
  print ('-no response-')

#  time.sleep(3)

print (' '  )
print( 'test 5, get value')
write(k_ID_5, k_CMD_exe_test, 0x00, 0, 0) 
time.sleep(0.1)
if(read()==0):
  print ('-no response-')

pdata = 0x0001
for y in range(0, 10):
  print ('data 0x%x'% pdata)
  write(k_ID_4, k_CMD_exe_test, 0x00, 4, pdata) # set led on
  pdata = pdata*2
  time.sleep(0.01)
  if(read()==0):
    print ('-no response-')
  #write(k_ID_5, k_CMD_exe_test, 0x00, 0, 0) 
  #time.sleep(0.05)
  #if(read()==0):
  #  print '-no response-'    
   
pdata = 0x0001
for y in range(0, 10):
  print( 'data 0x%x'% pdata)
  write(k_ID_3, k_CMD_exe_test, 0x00, 4, pdata) # set led off
  pdata = pdata*2
  time.sleep(0.01)
  if(read()==0):
    print ('-no response-')

   
# print( ' ' ) 
# print( 'test 5, get value')
# write(k_ID_5, k_CMD_exe_test, 0x00, 0, 0) 
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')

# print (' '  )
# print ('test 4, set low')
# pdata = 0x003F
# write(k_ID_4, k_CMD_exe_test, 0x00, 4, pdata) 
# time.sleep(1)
# if(read()==0):
#   print( '-no response-')

# print (' '  )
# print ('test 5, get value')
# write(k_ID_5, k_CMD_exe_test, 0x00, 0, 0) 
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')

#   print (' '  )
# print ('test 0, ok')
# pdata = ("TESTOK")
# write(k_ID_0, k_CMD_exe_test, 0x00, len(pdata), pdata) #demo test
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')

# print (' ' )
# print( 'test 0, fail')
# pdata = ("TESTFAIL")
# write(k_ID_0, k_CMD_exe_test, 0x00, len(pdata), pdata) # demo test
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')

  
# print( ' ' ) 
# print( 'get test parameter info, input parameter')
# write(k_ID_0, k_CMD_get_test_parameter_info, 0x00, 0x01, 0x00) # demo test
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')
  
# print (' ')
# print ('get test parameter info, response parameter')
# write(k_ID_0, k_CMD_get_test_parameter_info, 0x00, 0x01, 0x01) #demo test
# time.sleep(1)
# if(read()==0):
#   print ('-no response-')

# print (' ' )
# print ('get test case info')
# #id,  cmd, status, length, data
# #write(k_ID_DEFAULT, k_CMD_get_test_case_info, 0x00, 0x00, 0x00) #get test parameter info, input parameter
# write(k_ID_0, k_CMD_get_test_case_info, 0x00, 0x00, 0x00) #get test parameter info, input parameter
# time.sleep(1)
# if(read()==0):
#   print( '-no response-')

# print( ' ')
# close()

