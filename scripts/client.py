import json
import bluetooth

port = 0
# server socket bluetooth MAC Address
server_mac = 'XX:XX:XX:XX:XX:XX' 

def sendMessage(client_sock, userInput):
    client_sock.send(userInput)

# function that deserialized the json object recieved from the Central Hub (RPI 3B+) and mapping information about each instrument with a Serial No.
def showConnectedInstruments(client_sock):
    print("Connected Devices:")
    instrumentAddrDict = {}
    instrumentList = json.loads(client_sock.recv(1024))
    for i in range(0, len(instrumentList)):
        instrument = instrumentList[i]
        instr_name = instrument["instr_name"]
        instr_manufacturer = instrument["instr_manufacturer"]
        instr_addr = instrument["instr_addr"]
        instrumentAddrDict[i + 1] = instr_addr
        print("{}.Device: {}-{}, Address: {}".format( i + 1, instr_name, instr_manufacturer, instr_addr ))    
    return instrumentAddrDict
        

if __name__ == '__main__':
    # creating client socket 
    client_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    
    # connecting client socket to the server socket
    client_sock.connect(( server_mac, port ))
    print("Connected to server at: {}\n".format( server_mac ))
    
    # returns dictionary of connected instrument information with Serial No. 
    instrumentAddrDict = showConnectedInstruments( client_sock )
    
    print("\nIn order to send a SCPI Command, write <Sr No.> <SCPI Command>\nTo QUIT, press 'Q' or 'q'\n")
    
    try:
        while True:
            userInput = input("Command: ")
            if userInput == "Q" or userInput == "q":
                client_sock.close()
                print("Connection Closed.")
                break
            else:
                # Splitting the userInput <Sr No.> <SCPI Command> into a list : Serial No. & SCPI Command
                splittedUserInput = userInput.strip().split(";")
                for scpiCommands in splittedUserInput:
                    splittedSCPICommand = scpiCommands.strip().split(" ", 1)
                    instrumentAddr = instrumentAddrDict[int( splittedSCPICommand[0] )]
                    scpiCommand = splittedSCPICommand[1]
                
                    # In SCPI every query contains a "?". So segregatting each user command in either Query or Set
                    if scpiCommand.find("?") != -1:
                        sendMessage( client_sock, json.dumps({ "instrAddr" : instrumentAddr , "scpiCommand" : scpiCommand }) )
                        queryResponse = client_sock.recv(1024)
                        print("Response: {}".format( queryResponse.strip().decode('utf-8') ))
                    else:
                        sendMessage( client_sock, json.dumps({ "instrAddr" : instrumentAddr , "scpiCommand" : scpiCommand }) )
            
    except Exception as e:
        print("Exception occured. {}".format(e))
        
        

        
        
