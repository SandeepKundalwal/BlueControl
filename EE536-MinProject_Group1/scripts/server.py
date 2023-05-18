import json
import sys
import time
import datetime
import bluetooth
import logging as LOG
import pyvisa as visa

port = 0
LOG.basicConfig(filename='logger.log', format='%(asctime)s | %(message)s ', level = LOG.INFO, filemode='w')

class Instrument:
    def __init__(self, instr_name, instr_manufacturer, instr_UUID, instr_addr):
        self.instr_name = instr_name
        self.instr_manufacturer = instr_manufacturer
        self.instr_UUID = instr_UUID
        self.instr_addr = instr_addr

# define a custom encoder function to convert class objects to JSON-serializable
def encoder(obj):
    if isinstance(obj, Instrument):
        # convert Instrument object to a dictionary
        return {'instr_name':obj.instr_name, 'instr_manufacturer':obj.instr_manufacturer, 'instr_UUID':obj.instr_UUID, 'instr_addr':obj.instr_addr}
    # if the object is not a Instrument object, return the original object
    return obj


def sleep(duration):
    time.sleep(duration)


def acceptConnectionFromClient(server_sock):
    return server_sock.accept()


def createBindServerSocket():
    # Create a Bluetooth socket object using RFCOMM protocol
    server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    # Bind the socket to the current device
    server_sock.bind(( "", port ))
    return server_sock  


def connectedInstrumentsInformation(rm):
    # creating devices list
    instruments = []
    connected_instruments = rm.list_resources()
   
    for i in range(1, len(connected_instruments)):
        instr_addr = connected_instruments[i]
        instr_info = queryInstrument(instr_addr, "*IDN?").strip().split(",")
        instr_manufacturer = instr_info[0]
        instr_name = instr_info[1]
        instr_UUID = instr_info[2]
        instruments.append(Instrument(instr_name, instr_manufacturer, instr_UUID, instr_addr))
    
    return instruments

# Querying the instrument: 
#   instrAddr: Address of the instrument to query
#   scpiCommand: SCPI Command
def queryInstrument(instrAddr, scpiCommand):
    try:
        instrObj = rm.open_resource(instrAddr, read_termination='\n', write_termination='\n', encoding='latin1')
        instrObj.write(scpiCommand)
        # Added static delay as some query takes time to give response. NEED to make this better --future work
        sleep(10)
        response = instrObj.read()
        return response
    except visa.VisaIOError as e:
        return "An exception occured: " + e
    finally:
        instrObj.close()
        

# Setting a SCPI Command to the instrument: 
#   instrAddr: Address of the instrument to query
#   scpiCommand: SCPI Command 
def setInstrument(instrAddr, scpiCommand):
    try:
        sleep(2)
        instrObj = rm.open_resource(instrAddr, read_termination='\n', write_termination='\n')
        instrObj.write(scpiCommand)
        sleep(2)
    except visa.VisaIOError as e:
        print("An exception occured: {}".format(e))
        LOG.info("An exception occured " + e)
    finally:
        instrObj.close()


if __name__ == '__main__':
    # Py-VISA Object
    rm = visa.ResourceManager('@py')
    
    # creating and binding the server socket
    server_sock = createBindServerSocket()
        
    # Listen for incoming connections (with a maximum queue of 1)
    server_sock.listen(1)
        
    print("listening on port {}".format( port ))

    while True:
        try:
            # accepting connection from client
            client_sock, client_address = acceptConnectionFromClient( server_sock )
            print("{} | Connection Established with {}\n".format( str(datetime.datetime.now()), client_address ))
            LOG.info("Connection Established with " + str(client_address))


            # returns a list of connected instruments
            instruments = connectedInstrumentsInformation(rm)
            
            for instrument in instruments:
                instrName = instrument.instr_name
                instrManufacturer = instrument.instr_manufacturer
                instrUUID = instrument.instr_UUID
                instrAddr = instrument.instr_addr
                print("{} | Device Name:{} Manufacturer:{} Address:{}".format( str(datetime.datetime.now()), instrName, instrManufacturer, instrAddr ))
                LOG.info(instrName + " " + instrManufacturer + " " + instrUUID + " " + instrAddr)
            
            # serializing data as json object
            instruments_str = json.dumps( instruments, default=encoder )
            client_sock.send( instruments_str )

            while True:
                # json.loads() deserializes the json
                recievedCommand = json.loads( client_sock.recv(1024) )
                instrAddress = recievedCommand["instrAddr"]
                scpiCommand = recievedCommand["scpiCommand"]
            
                if scpiCommand.find("?") != -1:
                    response = queryInstrument( instrAddress, scpiCommand )
                    print("{} | FROM:{} TO:{} SCPI:{} query RESPONSE{}"
                            .format( str(datetime.datetime.now()), client_address, instrAddress, scpiCommand, response ))
                    LOG.info( "FROM:" + str(client_address) + " TO:" +
                            instrAddress +
                            " query SCPI:" +
                            scpiCommand + " RESPONSE:" +
                            response )
                    client_sock.send( response.encode('utf-8') )
                        
                else:
                    print("{} | FROM:{} TO:{} set SCPI:{}"
                            .format( str(datetime.datetime.now()), client_address, instrAddress, scpiCommand ))
                    setInstrument( instrAddress, scpiCommand ) 
                    LOG.info( "FROM:" + str(client_address) + " TO:" +
                            instrAddress +
                            " set SCPI:" +
                            scpiCommand )
                    
        except KeyboardInterrupt:
            print("Shutdown requested...exiting")
            LOG.info("[KeyboardInterrupt] Shutdown requested...exiting")
            sys.exit(0)
        except Exception as e:
            print("{} | Connection closed by {}\n".format( str(datetime.datetime.now()), client_address ))
            LOG.info("Connection closed by " + str(client_address))

