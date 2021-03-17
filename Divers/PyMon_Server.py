#! /usr/bin/env python
#
# ------------------------------ SERVER IRD -------------------------------- #
#
# - Conforme a "IRD_Specification_V_13"
#
# - Un device IRD s'authentifie en utilisant les trames:
#    IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST / IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE;
# - Le Control Panel se connecte au device en utilisant les trames:
#    IRD_PACKET__ASK_CONNECTION_INFO / IRD_PACKET__SEND_CONNECTION_INFO;
# - Le Control Panel dialogue avec le device via le serveur IRD avec les trames:
#    IRD_PACKET__SCPI_COMMAND.
# - Le serveur IRD gere une liste des devices et CP connectes, cette liste est
#    geree dynamiquement lors de la connexion et de la deconnexion d'un device (ou CP).
# - Chaque device (ou CP) doit emettre une requete toutes les 10 minutes sinon
#    le serveur le considere non connecte, et l'ejecte de la liste.
# - Le client (ou CP) utilise toujours le meme port pour communiquer avec le serveur.
#    Ce port ne doit etre fermee qu'en fin de session.
#
# -------------------------------------------------------------------------- #

#from Crypto.Cipher import AES
#from Crypto.Util.Padding import pad
from struct import unpack

import hashlib
import random
import sched
import socket
import time
import threading

# /************************** SERVER IRD  **************************/
# NETWORK CONFIG
# /*****************************************************************/

#IrdServerAddressIp = '10.3.212.46'
IrdServerAddressIp = '127.0.0.0'
IrdGatewayAddress = '10.3.10.1'
IrdMaskAddress = '255.255.0.0'
IrdServerPort = 3041

# /*****************************************************************/
# DEFINE
# /*****************************************************************/
APP_NAME = "PyMon_Server"
VERSION = "0.01"
AUTHOR = "PLE"
DATE = "2021/03/16"

TITLE_COLOR = "\033[1;1m"
STANDARD_COLOR = "\033[1;0m"

MASK_THIRD_BYTES = 0xFF0000
MASK_SECOND_BYTES = 0xFF00
MASK_FIRST_BYTES = 0xFF

INDEX_SERVER_IRD = 0

MAX_PACKET_SIZE = 1000000

IRD_PACKET__HEARTBEAT = 0xFFFFFFFF
IRD_PACKET__NACK = 0x00000000
IRD_PACKET__ACK = 0x00000001
IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST = 0x00001000
IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE = 0x00001001
IRD_PACKET__ASK_CONNECTION_INFO = 0x00001002
IRD_PACKET__SEND_CONNECTION_INFO = 0x00001003
IRD_PACKET__SCPI_COMMAND = 0x00001100

IPV4_ADDRESS = 0
IPV6_ADDRESS = 1

IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__FRAME_SIZE = 132
IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__HEADER_SIZE = 36
IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__PAYLOAD_SIZE = 64

IRD_PACKET__SEND_CONNECTION_INFO__FRAME_SIZE = 240
IRD_PACKET__SEND_CONNECTION_INFO__HEADER_SIZE = 36
IRD_PACKET__SEND_CONNECTION_INFO__PAYLOAD_SIZE = 184

IRD_PACKET__ACK__LENGTH = 19
IRD_PACKET__NACK__LENGTH = 20

TIMEOUT_INIT = 10

ENCRYPT_KEY_HEADER = "+-=$<"
ENCRYPT_KEY_FOOTER = ">!*&"

# Liste des connexions et de leurs caracteristiques
ConnectionInfosList = [ {} for i in range(10) ]

#*****************************************************************
# TOOL FUNCTIONS
#*****************************************************************


# Construction d'un bytearray contenant un seul octet
def BuildOneByte(Value):
    if Value == -1:
        List = [255]
    else:
        List = [Value]
    return bytearray(List)


# Construction d'un bytearray contenant 4 octets
# Utilise pour convertire en entier vers un bytearray
def BuildFourBytes(Value):
    if Value == -1:
        List = [255, 255, 255, 255]
    else:
        List = [(Value & MASK_FIRST_BYTES), (Value & MASK_SECOND_BYTES) >> 8, (Value & MASK_THIRD_BYTES) >> 16, Value >> 24]
    return bytearray(List)


# Conversion d'une adresse IP vers un bytearray (voir spec IRD V12)
def BuildIp(Word, AddressType):
    if AddressType == IPV4_ADDRESS:
        List = [int(i) for i in Word.split('.')]
        PaddingList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        FinalList = List + PaddingList
    elif AddressType == IPV6_ADDRESS:
        # TO DO
        FinalList = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    return bytearray(FinalList)


# Conversion d'une adresse IP codee en IRV-V12 vers une chaine de caracteres
def UnpackIp(Value):
    returnedValue = str(Value & MASK_FIRST_BYTES) + '.' + str((Value & MASK_SECOND_BYTES) >> 8) + '.' + str((Value & MASK_THIRD_BYTES) >> 16) + '.' + str(Value >> 24)
    return returnedValue


# Construction d'une trame IRD_PACKET__ACK
def buildFrameACK():
        PacketId = BuildFourBytes(IRD_PACKET__ACK)
        PacketSize = BuildFourBytes(IRD_PACKET__ACK__LENGTH)
        IndexSrc = BuildFourBytes(0)
        MessageLength = BuildFourBytes(4)
        Message = bytearray('ACK', 'ascii')

        FrameToSend = PacketId + PacketSize + IndexSrc + MessageLength + Message
        return FrameToSend


# Construction d'une trame IRD_PACKET__NACK
def buildFrameNACK():
        PacketId = BuildFourBytes(IRD_PACKET__NACK)
        PacketSize = BuildFourBytes(IRD_PACKET__NACK__LENGTH)
        IndexSrc = BuildFourBytes(0)
        MessageLength = BuildFourBytes(4)
        Message = bytearray('NACK', 'ascii')

        FrameToSend = PacketId + PacketSize + IndexSrc + MessageLength + Message
        return FrameToSend

# /*********************** END TOOL FUNCTION ************************/


#
# Lecture, Parsing Et Traitement de la requete dans un thread independant
#
def readParseRequestFromClient(ConnectedSocket, Client):

    print("<== Connection requested from {}".format(Client))

    while True:

        Frame = readFrame(ConnectedSocket)


        if Frame:

            # Parsing du header de la requete IRD
            ParsedFrame = ParseFrameHeader(Frame)

            if 'IndexSource' in ParsedFrame:
                IndexSrc = ParsedFrame['IndexSource']
                device = ConnectionInfosList[IndexSrc]
                device['Timeout'] = TIMEOUT_INIT

            else:
                # Certaines trames ACK, NACK ne contiennent pas le champ 'IndexSrc'
                IndexSrc = 2 # Unregistered device

            if'SecurityLevel' in ParsedFrame:
                SecurityLevel = ParsedFrame['SecurityLevel']

            else:
                # Certaines trames ACK, NACK, HEARTBEAT ne contiennent pas le champ 'SecurityLevel'
                SecurityLevel = 'CLR\0'

            try:
                if ParsedFrame['PacketId'] == IRD_PACKET__SCPI_COMMAND:
                    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print('<-> Frame received from device (or CP) and sent to CP (or device):')

                    try:
                        sessionKey = device['SessionKey']

                        # Decryptage de la requete IRD
                        Frame = decryptFrame(Frame, SecurityLevel, sessionKey)
                        ParseFrame(Frame)

                        # Les trames en provenance de la source sont dirigees vers la destination
                        destDescriptor = ConnectionInfosList[ParsedFrame['IndexDest']]
                        destSocket = destDescriptor['Socket']

                        if destDescriptor['Timeout'] > 0:
                            Frame = encryptFrame(Frame, destDescriptor['SecurityLevel'], \
                                             destDescriptor['SessionKey'])
                            destSocket.send(Frame)

                        else:
                            # Le destinataire a ete deconnecte => NACK
                            FrameToSend = buildFrameNACK()
                            ConnectedSocket.send(FrameToSend)

                    except KeyError:
                        # Le destinataire n'existe pas => NACK
                        FrameToSend = buildFrameNACK()
                        ConnectedSocket.send(FrameToSend)

                elif ParsedFrame['PacketId'] == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST or \
                     ParsedFrame['PacketId'] == IRD_PACKET__ASK_CONNECTION_INFO:
                    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print('<-- Frame received:')

                    # La cle de session est calculee d'apres le S/N
                    sessionKey = ENCRYPT_KEY_HEADER + ParsedFrame['WarrantyNumber'].replace('\0', '') + \
                                ENCRYPT_KEY_FOOTER
                    sessionKey = hashlib.md5(sessionKey.encode('ascii')).digest()

                    # Decryptage de la requete IRD
                    Frame = decryptFrame(Frame, SecurityLevel, sessionKey)
                    ParsedFrame = ParseFrame(Frame)

                    # Traitement de la requete IRD
                    FrameToSend = DigestFrame(ParsedFrame, ConnectedSocket)

                    if FrameToSend != '':
                        # Emission d'une reponse a la requete
                        print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        print('--> Frame sent:')
                        ParseFrame(FrameToSend)

                        # Encryptage de la reponse IRD
                        FrameToSend = encryptFrame(FrameToSend, SecurityLevel, sessionKey)
                        ConnectedSocket.send(FrameToSend)

                    else:
                        print('ERROR: Frame received: not conform')

                elif ParsedFrame['PacketId'] == IRD_PACKET__HEARTBEAT:
                    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print('<-- Frame received:')
                    ParsedFrame = ParseFrame(Frame)

                    # Traitement de la requete IRD
                    FrameToSend = DigestFrame(ParsedFrame, ConnectedSocket)

                    print('--> Frame sent:')
                    ParseFrame(FrameToSend)
                    ConnectedSocket.send(FrameToSend)

                elif ParsedFrame['PacketId'] == IRD_PACKET__ACK or \
                    ParsedFrame['PacketId'] == IRD_PACKET__NACK:
                    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print('<-> Frame received from device (or CP) and sent to CP (or device):')
                    ParsedFrame = ParseFrame(Frame)

                    # Les trames en provenance de la source sont dirigees vers la destination
                    destDescriptor = ConnectionInfosList[ParsedFrame['IndexDest']]
                    destSocket = destDescriptor['Socket']

                    destSocket.send(Frame)

                else:
                    print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                    print('<-- Frame received:')

                    sessionKey = device['SessionKey']

                    # Decryptage de la requete IRD
                    Frame = decryptFrame(Frame, SecurityLevel, sessionKey)
                    ParsedFrame = ParseFrame(Frame)

                    # Traitement de la requete IRD
                    FrameToSend = DigestFrame(ParsedFrame, ConnectedSocket)

                    if FrameToSend != '':
                        # Emission d'une reponse a la requete
                        print('=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
                        print('--> Frame sent:')
                        ParseFrame(FrameToSend)

                        # Encryptage de la reponse IRD
                        FrameToSend = encryptFrame(FrameToSend, SecurityLevel, sessionKey)
                        ConnectedSocket.send(FrameToSend)

            except KeyError:
                continue

        else:
            break

    # Recherche du periph connecte sur ce socket dans la liste des devices et CP connectes
    for device in ConnectionInfosList:
        try:
            if device['Socket'] == ConnectedSocket:
                device['Socket'] = 0
                device['Timeout'] = 0
        except:
            continue


    print("==> Connection with {} closed".format(Client))
    ConnectedSocket.close()


#
# Lecture d'une trame complete
#
def readFrame(SocketToRead):

    try:
        # Lecture du header de la trame
        DeviceData = SocketToRead.recv(8);

        if DeviceData:
            Frame = DeviceData

            # Lecture d'infos dans le header de la trame
            Field = unpack('I', Frame[4:8])
            PacketSize = Field[0] - 8

            # Lecture du reste de la trame
            while PacketSize > 0:
                DeviceData = SocketToRead.recv(PacketSize)

                if DeviceData:
                    Frame += DeviceData
                else:
                    Frame = ''
                    break
                PacketSize -= len(DeviceData)
        else:
            Frame = ''

    except:
        Frame = ''

    return Frame


#
# Cryptage d'une trame en utilisant la cle de session.
#
def encryptFrame(Frame, SecurityLevel, SessionKey):

    EncryptedFrame = {}

    PacketId = unpack('I', Frame[0:4])[0]
    if PacketId == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST or \
       PacketId == IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE or \
       PacketId == IRD_PACKET__ASK_CONNECTION_INFO or \
       PacketId == IRD_PACKET__SEND_CONNECTION_INFO or \
       PacketId == IRD_PACKET__SCPI_COMMAND:
        HeaderSize = unpack('I', Frame[16:20])[0]

        if SecurityLevel == 'SAS\0':
            # Padding
            EncryptedBuffer = pad(Frame[HeaderSize + 16:], AES.block_size)

            cipher = AES.new(SessionKey, AES.MODE_CBC)
            EncryptedBuffer = cipher.encrypt(EncryptedBuffer)

            # la taille de la trame est ajustee
            frameSize = HeaderSize + 16 + len(EncryptedBuffer)

            EncryptedFrame = Frame[0:4] + BuildFourBytes(frameSize) + \
                             Frame[8:20] + bytearray('SAS\0', 'ascii') + \
                             Frame[24:HeaderSize] + cipher.iv + EncryptedBuffer

            print('--> FRAME ENCRYPTED <--')

        else:
            # Pas de Padding
            EncryptedFrame = Frame[0:20] + bytearray('CLR\0', 'ascii') + \
                             Frame[24:]

            print('--> FRAME NOT ENCRYPTED <--')
    else:
        EncryptedFrame = Frame

    return EncryptedFrame


#
# Decryptage d'une trame en utilisant la cle de session.
#
def decryptFrame(Frame, SecurityLevel, SessionKey):

    DecryptedFrame = {}
    if SecurityLevel == 'SAS\0':
        PacketId = unpack('I', Frame[0:4])[0]

        if PacketId == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST or \
           PacketId == IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE or \
           PacketId == IRD_PACKET__ASK_CONNECTION_INFO or \
           PacketId == IRD_PACKET__SEND_CONNECTION_INFO or \
           PacketId == IRD_PACKET__SCPI_COMMAND:

            HeaderSize = unpack('I', Frame[16:20])[0]

            InitVector = Frame[HeaderSize:HeaderSize + 16]

            cipher = AES.new(SessionKey, AES.MODE_CBC, InitVector)
            DecryptedBuffer = cipher.decrypt(Frame[HeaderSize + 16:])

            DecryptedFrame = Frame[0:HeaderSize + 16] + DecryptedBuffer
        else:
            DecryptedFrame = Frame
    else:
        DecryptedFrame = Frame

    return DecryptedFrame


#
# Parsing du header d'une d'une trame
#
def ParseFrameHeader(Frame):
    ParsedFrame = {}

    Field = unpack('I', Frame[0:4])
    ParsedFrame['PacketId'] = Field[0]

    Field = unpack('I', Frame[4:8])
    ParsedFrame['PacketSize'] = Field[0]

    # Des champs supplementaires sont decodes dans le header de IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST
    # et IRD_PACKET__ASK_CONNECTION_INFO
    # - IndexSource
    # - IndexDest
    # - WarrantyNumber
    # - SecurityLevel
    if ParsedFrame['PacketId'] == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST or \
       ParsedFrame['PacketId'] == IRD_PACKET__ASK_CONNECTION_INFO:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')

        Field = unpack('20s', Frame[36:56])
        ParsedFrame['WarrantyNumber'] = Field[0].decode('ascii')

    # Des champs supplementaires sont decodes dans le header IRD_PACKET__SCPI_COMMAND:
    # - IndexSource
    # - IndexDest
    # - SecurityLevel
    elif  ParsedFrame['PacketId'] == IRD_PACKET__SCPI_COMMAND:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')

    # Des champs supplementaires sont decodes dans le header de IRD_PACKET__HEARTBEAT:
    # - IndexSource
    elif ParsedFrame['PacketId'] == IRD_PACKET__HEARTBEAT:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]

    # Des champs supplementaires sont decodes dans le header de
    #  IRD_PACKET__NACK et IRD_PACKET__ACK
    # - IndexSource
    elif ParsedFrame['PacketId'] == IRD_PACKET__NACK or \
         ParsedFrame['PacketId'] == IRD_PACKET__ACK:
        ParsedFrame['IndexDest'] = Field[0]

    return ParsedFrame


#
# Decodage d'une trame et Affichage de la valeur de chaque champ
#
def ParseFrame(Frame):
    ParsedFrame = {}

    Field = unpack('I', Frame[0:4])
    packetId = Field[0]

    ParsedFrame['PacketId'] = packetId
    print('        Command ID =', hex(ParsedFrame['PacketId']))

    Field = unpack('I', Frame[4:8])
    ParsedFrame['PacketSize'] = Field[0]
    print('        Packet Size =', ParsedFrame['PacketSize'])

    if packetId == IRD_PACKET__HEARTBEAT:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Socket Index =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['MessageLength'] = Field[0]
        print('        Message Length =', ParsedFrame['MessageLength'])

        Length = ParsedFrame['MessageLength'] - 5
        Field = unpack('%ds' % Length, Frame[16:16 + Length])
        ParsedFrame['Message'] = Field[0].decode('ascii')
        print('        Message =', ParsedFrame['Message'])

    elif packetId == IRD_PACKET__ACK:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Socket Index =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['MessageLength'] = Field[0]
        print('        Message Length =', ParsedFrame['MessageLength'])

    elif packetId == IRD_PACKET__NACK:
        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Socket Index =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['MessageLength'] = Field[0]
        print('        Message Length =', ParsedFrame['MessageLength'])

    elif packetId == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST:

        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Index Source =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Index Destination =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[16:20])
        ParsedFrame['HeaderSize'] = Field[0]
        print('        HeaderSize =', ParsedFrame['HeaderSize'])

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')
        print('        Security Level =' , ParsedFrame['SecurityLevel'])

        Field = unpack('I', Frame[24:28])
        ParsedFrame['TotalDataSize'] = Field[0]
        print('        Total Data Size =' , ParsedFrame['TotalDataSize'])

        Field = unpack('I', Frame[28:32])
        ParsedFrame['BlockIndex'] = Field[0]
        print('        Block Index =' , ParsedFrame['BlockIndex'])

        Field = unpack('I', Frame[32:36])
        ParsedFrame['BlockNumber'] = Field[0]
        print('        Block Number =' , ParsedFrame['BlockNumber'])

        Field = unpack('20s', Frame[36:56])
        ParsedFrame['WarrantyNumber'] = Field[0].decode('ascii')
        print('        Warranty Number =', ParsedFrame['WarrantyNumber'])

        # Les caracteres NULL sont retires de la cle
        # Puis la cle est encadre du header et du footer
        # Puis elle est complete de caracteres NULL pour obtenir 32 caracteres
        encryptKey = ENCRYPT_KEY_HEADER + ParsedFrame['WarrantyNumber'].replace('\0','') + \
                     ENCRYPT_KEY_FOOTER
        ParsedFrame['SessionKey'] = hashlib.md5(encryptKey.encode('ascii')).digest()
        print('       *Session Key* =', hashlib.md5(encryptKey.encode('ascii')).hexdigest())

        Field = unpack('I', Frame[72:76])
        ParsedFrame['PayloadLength'] = Field[0]
        print('        Payload Length =', ParsedFrame['PayloadLength'])

        Field = unpack('I', Frame[76:80])
        ParsedFrame['AddressType'] = Field[0]
        print('        AddressType =', ParsedFrame['AddressType'])

        Field = unpack('IIII', Frame[80:96])
        ParsedFrame['IpAddress'] = UnpackIp(Field[0])
        print('        IP Address=', ParsedFrame['IpAddress'])

        Field = unpack('IIII', Frame[96:112])
        ParsedFrame['GatewayAddress'] = UnpackIp(Field[0])
        print('        Gateway Address =', ParsedFrame['GatewayAddress'])

        Field = unpack('IIII', Frame[112:128])
        ParsedFrame['SubnetMask'] = UnpackIp(Field[0])
        print('        Mask Address =', ParsedFrame['SubnetMask'])

        Field = unpack('I', Frame[128:132])
        ParsedFrame['Port'] = Field[0]
        print('        Port =', ParsedFrame['Port'])

        Field = unpack('32s', Frame[132:164])
        ParsedFrame['Password'] = Field[0].decode("ascii")
        print('        Password =', ParsedFrame['Password'])

        Field = unpack('I', Frame[164:168])
        ParsedFrame['MaxPacketSize'] = Field[0]
        print('        Max Packet Size =', ParsedFrame['MaxPacketSize'])

    elif packetId == IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE:

        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Index Source =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Index Destination =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[16:20])
        ParsedFrame['HeaderSize'] = Field[0]
        print('        HeaderSize =', ParsedFrame['HeaderSize'])

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')
        print('        Security Level =' , ParsedFrame['SecurityLevel'])

        Field = unpack('I', Frame[24:28])
        ParsedFrame['TotalDataSize'] = Field[0]
        print('        Total Data Size =' , ParsedFrame['TotalDataSize'])

        Field = unpack('I', Frame[28:32])
        ParsedFrame['BlockIndex'] = Field[0]
        print('        Block Index =' , ParsedFrame['BlockIndex'])

        Field = unpack('I', Frame[32:36])
        ParsedFrame['BlockNumber'] = Field[0]
        print('        Block Number =' , ParsedFrame['BlockNumber'])

        Field = unpack('I', Frame[52:56])
        ParsedFrame['PayloadLength'] = Field[0]
        print('        Payload Length =', ParsedFrame['PayloadLength'])

        Field = unpack('I', Frame[56:60])
        ParsedFrame['AddressType'] = Field[0]
        print('        AddressType =', ParsedFrame['AddressType'])

        Field = unpack('IIII', Frame[60:76])
        ParsedFrame['IpAddress'] = UnpackIp(Field[0])
        print('        IP Address=', ParsedFrame['IpAddress'])

        Field = unpack('IIII', Frame[76:92])
        ParsedFrame['GatewayAddress'] = UnpackIp(Field[0])
        print('        Gateway Address =', ParsedFrame['GatewayAddress'])

        Field = unpack('IIII', Frame[92:108])
        ParsedFrame['SubnetMask'] = UnpackIp(Field[0])
        print('        Mask Address =', ParsedFrame['SubnetMask'])

        Field = unpack('I', Frame[108:112])
        ParsedFrame['Port'] = Field[0]
        print('        Port =', ParsedFrame['Port'])

        Field = unpack('I', Frame[112:116])
        ParsedFrame['MaxPacketSize'] = Field[0]
        print('        Max Packet Size =', ParsedFrame['MaxPacketSize'])

    elif packetId == IRD_PACKET__ASK_CONNECTION_INFO:

        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Index Source =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Index Destination =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[16:20])
        ParsedFrame['HeaderSize'] = Field[0]
        print('        HeaderSize =', ParsedFrame['HeaderSize'])

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')
        print('        Security Level =' , ParsedFrame['SecurityLevel'])

        Field = unpack('I', Frame[24:28])
        ParsedFrame['TotalDataSize'] = Field[0]
        print('        Total Data Size =' , ParsedFrame['TotalDataSize'])

        Field = unpack('I', Frame[28:32])
        ParsedFrame['BlockIndex'] = Field[0]
        print('        Block Index =' , ParsedFrame['BlockIndex'])

        Field = unpack('I', Frame[32:36])
        ParsedFrame['BlockNumber'] = Field[0]
        print('        Block Number =' , ParsedFrame['BlockNumber'])

        Field = unpack('20s', Frame[36:56])
        ParsedFrame['WarrantyNumber'] = Field[0].decode("ascii")
        print('        Warranty Number =' , ParsedFrame['WarrantyNumber'])

        # Les caracteres NULL sont retires de la cle
        # Puis la cle est encadre du header et du footer
        # Puis elle est complete de caracteres NULL pour obtenir 32 caracteres
        encryptKey = ENCRYPT_KEY_HEADER + ParsedFrame['WarrantyNumber'].replace('\0','') + \
                     ENCRYPT_KEY_FOOTER
        ParsedFrame['SessionKey'] = hashlib.md5(encryptKey.encode('ascii')).digest()
        print('       *Session Key* =', hashlib.md5(encryptKey.encode('ascii')).hexdigest())

        Field = unpack('I', Frame[72:76])
        ParsedFrame['PayloadLength'] = Field[0]
        print('        Payload Length =', ParsedFrame['PayloadLength'])

        Field = unpack('20s', Frame[76:96])
        ParsedFrame['DeviceWarranty'] = Field[0].decode("ascii")
        print('        Device Warranty =', ParsedFrame['DeviceWarranty'])

        Field = unpack('32s', Frame[96:128])
        ParsedFrame['Password'] = Field[0].decode("ascii")
        print('        Password =', ParsedFrame['Password'])

    elif packetId == IRD_PACKET__SEND_CONNECTION_INFO:

        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Index Source =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Index Destination =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[16:20])
        ParsedFrame['HeaderSize'] = Field[0]
        print('        HeaderSize =', ParsedFrame['HeaderSize'])

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')
        print('        Security Level =' , ParsedFrame['SecurityLevel'])

        Field = unpack('I', Frame[24:28])
        ParsedFrame['TotalDataSize'] = Field[0]
        print('        Total Data Size =' , ParsedFrame['TotalDataSize'])

        Field = unpack('I', Frame[28:32])
        ParsedFrame['BlockIndex'] = Field[0]
        print('        Block Index =' , ParsedFrame['BlockIndex'])

        Field = unpack('I', Frame[32:36])
        ParsedFrame['BlockNumber'] = Field[0]
        print('        Block Number =' , ParsedFrame['BlockNumber'])

        Field = unpack('I', Frame[52:56])
        ParsedFrame['PayloadLength'] = Field[0]
        print('        Payload Length =', ParsedFrame['PayloadLength'])

        Field = unpack('I', Frame[56:60])
        DeviceIndex = Field[0]
        print('        Device Index =', DeviceIndex)

        Field = unpack('100s', Frame[60:160])
        ParsedFrame['DeviceName'] = Field[0].decode('ascii')
        print('        Device Name =', ParsedFrame['DeviceName'])

        Field = unpack('20s', Frame[160:180])
        ParsedFrame['WarrantyNumber'] = Field[0].decode('ascii')
        print('        Warranty Number =', ParsedFrame['WarrantyNumber'])

        Field = unpack('I', Frame[180:184])
        ParsedFrame['AddressType'] = Field[0]
        print('        Address Type =', ParsedFrame['AddressType'])

        Field = unpack('IIII', Frame[184:200])
        ParsedFrame['IpAddress'] = UnpackIp(Field[0])
        print('        IP Address=', ParsedFrame['IpAddress'])

        Field = unpack('IIII', Frame[200:216])
        ParsedFrame['GatewayAddress'] = UnpackIp(Field[0])
        print('        Gateway Address =', ParsedFrame['GatewayAddress'])

        Field = unpack('IIII', Frame[216:232])
        ParsedFrame['SubnetMask'] = UnpackIp(Field[0])
        print('        Mask Address =', ParsedFrame['SubnetMask'])

        Field = unpack('I', Frame[232:236])
        ParsedFrame['Port'] = Field[0]
        print('        Port =', ParsedFrame['Port'])

        Field = unpack('I', Frame[236:240])
        ParsedFrame['MaxPacketSize'] = Field[0]
        print('        Max Packet Size =', ParsedFrame['MaxPacketSize'])

    elif packetId == IRD_PACKET__SCPI_COMMAND:

        Field = unpack('I', Frame[8:12])
        ParsedFrame['IndexSource'] = Field[0]
        print('        Index Source =', ParsedFrame['IndexSource'])

        Field = unpack('I', Frame[12:16])
        ParsedFrame['IndexDest'] = Field[0]
        print('        Index Destination =', ParsedFrame['IndexDest'])

        Field = unpack('I', Frame[16:20])
        ParsedFrame['HeaderSize'] = Field[0]
        print('        HeaderSize =', ParsedFrame['HeaderSize'])

        Field = unpack('4s', Frame[20:24])
        ParsedFrame['SecurityLevel'] = Field[0].decode('ascii')
        print('        Security Level =' , ParsedFrame['SecurityLevel'])

        Field = unpack('I', Frame[24:28])
        ParsedFrame['TotalDataSize'] = Field[0]
        print('        Total Data Size =' , ParsedFrame['TotalDataSize'])

        Field = unpack('I', Frame[28:32])
        ParsedFrame['BlockIndex'] = Field[0]
        print('        Block Index =' , ParsedFrame['BlockIndex'])

        Field = unpack('I', Frame[32:36])
        ParsedFrame['BlockNumber'] = Field[0]
        print('        Block Number =' , ParsedFrame['BlockNumber'])

        Field = unpack('I', Frame[52:56])
        ParsedFrame['PayloadLength'] = Field[0]
        print('        Payload Length =', ParsedFrame['PayloadLength'])

        Field = unpack('4b', Frame[56:60])
        ParsedFrame['Reserved'] = Field[0]
        print('        Reserved =', ParsedFrame['Reserved'])

        Length = ParsedFrame['PayloadLength'] - 8
        Field = unpack('%ds' % Length, Frame[60:60 + Length])
        ParsedFrame['ScpiCommand'] = Field[0].decode('ascii')
        print('        SCPI Command =')
        if Length > 250 :
            # Affichage des 100 premiers caracteres
            print(ParsedFrame['ScpiCommand'][0:100],'\n...')

            # Affichage des 100 derniers caracteres
            print(ParsedFrame['ScpiCommand'][Length - 100:Length])
        else:
            print(ParsedFrame['ScpiCommand'])

    else:
        print('        Trame {} non decodee'.format(packetId))

    return ParsedFrame


#
# Traitement d'une trame recue
# Retourne la trame construite et un booleen qui vaut true s'il faut attendre une reponse du demandeur
#
def DigestFrame(ParsedFrame, Socket):

    FrameToSend = ''

    if ParsedFrame['PacketId'] == IRD_PACKET__HEARTBEAT:
        # Reponse a la commande HEARTBEAT => ACK
        FrameToSend = buildFrameACK()

    elif ParsedFrame['PacketId'] == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST:

        # Le device a-t-il deja ete enregistre?
        Index = -1
        for device in ConnectionInfosList:
            try:
                if device['Timeout'] != 0 and \
                   device['Socket'] == Socket:
                    Index = ConnectionInfosList.index(device)
                    break
            except:
                continue

        # Le device n'a pas encore ete enregistre
        if Index < 0:
            # Memorisation du socket pour les echanges futurs
            ParsedFrame['Socket'] = Socket

            # Initialisation du timeout associe au device ou CP
            ParsedFrame['Timeout'] = TIMEOUT_INIT

            # Recherche d'un emplacement libre dans la liste des devices et CPs
            for device in ConnectionInfosList:
                try:
                    if device[ 'Timeout'] == 0:
                        Index = ConnectionInfosList.index(device)
                        break
                except:
                    continue

            if Index < 0:
                # Enregistrement en fin de table
                ConnectionInfosList.append(ParsedFrame)
                Index = ConnectionInfosList.index(ParsedFrame)

            else:
                # Enregistrement dans l'emplacement libre de la table
                ConnectionInfosList[ Index ] = ParsedFrame

        # Preparation de la reponse a la requete
        PacketId = BuildFourBytes(IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE)
        PacketSize = BuildFourBytes(IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__FRAME_SIZE)
        IndexSrc = BuildFourBytes(INDEX_SERVER_IRD)
        IndexDest = BuildFourBytes(Index)
        HeaderSize = BuildFourBytes(IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__HEADER_SIZE)
        SecurityLevel = bytearray('CLR\0', 'ascii')
        TotalDataSize = BuildFourBytes(0)
        BlockIndex = BuildFourBytes(1)
        BlockNumber = BuildFourBytes(1)
        RandomStr = ''.join([chr(random.randint(0, 0x7F)) for i in range(16)])
        InitVector = bytearray(RandomStr, 'ascii')
        PayloadLength = BuildFourBytes(IRD_PACKET__AUTHENTIFICATION_INFO_RESPONSE__PAYLOAD_SIZE)
        AddressType = BuildFourBytes(IPV4_ADDRESS)
        IpAddress = BuildIp(ParsedFrame['IpAddress'], IPV4_ADDRESS)
        GatewayAddress = BuildIp(ParsedFrame['GatewayAddress'], IPV4_ADDRESS)
        SubnetMask = BuildIp(ParsedFrame['SubnetMask'], IPV4_ADDRESS)
        Port = BuildFourBytes(ParsedFrame['Port'])
        MaxPacketSize = BuildFourBytes(MAX_PACKET_SIZE)

        FrameToSend = PacketId + PacketSize + IndexSrc + IndexDest + HeaderSize + \
                      SecurityLevel + TotalDataSize + BlockIndex + BlockNumber + \
                      InitVector + PayloadLength + AddressType + \
                      IpAddress + GatewayAddress + SubnetMask + Port + MaxPacketSize

    elif ParsedFrame['PacketId'] == IRD_PACKET__ASK_CONNECTION_INFO:
        # Le control-panel a-t'il ete deja enregistre?
        IndexCp = -1
        for device in ConnectionInfosList:
            try:
                if ParsedFrame['Socket'] == Socket:
                    IndexCp = ConnectionInfosList.index(device)
                    break
            except KeyError:
                continue

        # Le control-panel  n'a pas encore ete enregistre
        if IndexCp < 0:
            # Memorisation du socket pour les echanges futurs
            ParsedFrame['Socket'] = Socket

            # Initialisation du timeout associe au device ou CP
            ParsedFrame['Timeout'] = TIMEOUT_INIT

            # Recherche d'un emplacement libre dans la liste des devices et CPs
            for device in ConnectionInfosList:
                try:
                    if device[ 'Timeout'] == 0:
                        IndexCp = ConnectionInfosList.index(device)
                        break
                except:
                    continue

            if IndexCp < 0:
                # Enregistrement en fin de table
                ConnectionInfosList.append(ParsedFrame)
                IndexCp = ConnectionInfosList.index(ParsedFrame)

            else:
                # Enregistrement dans l'emplacement libre de la table
                ConnectionInfosList[ IndexCp ] = ParsedFrame

        # Recherche du device dans la liste des devices connectes
        deviceFound = False
        for device in ConnectionInfosList:
            try:
                if device['PacketId'] == IRD_PACKET__AUTHENTIFICATION_INFO_REQUEST and \
                   device['WarrantyNumber'] == ParsedFrame['WarrantyNumber'] and \
                   device['Password'] == ParsedFrame['Password']:
                    deviceFound = True
                    break
            except KeyError:
                continue

        if deviceFound:
            # Device found => Frame  IRD_PACKET__SEND_CONNECTION_INFO
            PacketId = BuildFourBytes(IRD_PACKET__SEND_CONNECTION_INFO)
            PacketSize = BuildFourBytes(IRD_PACKET__SEND_CONNECTION_INFO__FRAME_SIZE)
            IndexSrc = BuildFourBytes(INDEX_SERVER_IRD)
            IndexCP = BuildFourBytes(IndexCp)
            HeaderSize = BuildFourBytes(IRD_PACKET__SEND_CONNECTION_INFO__HEADER_SIZE)
            SecurityLevel = bytearray('CLR\0', 'ascii')
            TotalDataSize = BuildFourBytes(0)
            BlockIndex = BuildFourBytes(1)
            BlockNumber = BuildFourBytes(1)
            RandomStr = ''.join([chr(random.randint(0, 0x7F)) for i in range(16)])
            InitVector = bytearray(RandomStr, 'ascii')
            PayloadLength = BuildFourBytes(IRD_PACKET__SEND_CONNECTION_INFO__PAYLOAD_SIZE)
            DeviceIndex = BuildFourBytes(ConnectionInfosList.index(device))
            DeviceName = bytearray('\0', 'ascii') * 100
            WarrantyNumber = bytearray(device['WarrantyNumber'], 'ascii')
            AddressType = BuildFourBytes(IPV4_ADDRESS)
            IpAddress = BuildIp(device['IpAddress'], IPV4_ADDRESS)
            GatewayAddress = BuildIp(device['GatewayAddress'], IPV4_ADDRESS)
            SubnetMask = BuildIp(device['SubnetMask'], IPV4_ADDRESS)
            Port = BuildFourBytes(int(device['Port']))
            MaxPacketSize = BuildFourBytes(MAX_PACKET_SIZE)

            FrameToSend = PacketId + PacketSize + IndexSrc + IndexCP + HeaderSize + \
                          SecurityLevel + TotalDataSize + BlockIndex + BlockNumber + \
                          InitVector + PayloadLength + DeviceIndex + \
                          DeviceName + WarrantyNumber + AddressType + IpAddress + \
                          GatewayAddress + SubnetMask + Port + MaxPacketSize

        else:
            # Device not found => NACK
            FrameToSend = buildFrameNACK()
    else:
        # Unknowned frame (or unsupported frame) => NACK
        FrameToSend = buildFrameNACK()

    return FrameToSend


# Ce thread surveille l'activite de chaque device et CP
def ConnectionSpy():
    # La fonction checkDeviceAndCPConnection gere le timeout de 10 min,
    # accorde au devices et CP
    Scheduler = sched.scheduler(time.time, time.sleep)
    Scheduler.enter(60, 1, checkDeviceAndCPConnection, (Scheduler,))
    Scheduler.run()


#
# Un timeout de 10 min est accorde a chaque device et control-panel.
# Ce thread se reveille toutes les minutes et verifie cette condition.
# La verification consiste a decrementer le champ Timeout de chaque item du
# tableau ConnectionInfosList.
# Si cette variable atteint la valeur 0, le device (ou CP) est retire du tableau
# ConnectionInfosList
#
def checkDeviceAndCPConnection(scheduler):
    # Scrutation de la liste des devices et CP connectes
    for device in ConnectionInfosList:
        try:
            timeout = device['Timeout']

            if timeout == 1:
                # Le device (ou CP) est deconnecte
                print('==>Device disconnected:', device['IpAddress'])
                device['Timeout'] = 0
                device['Socket'].shutdown(socket.SHUT_RDWR)
                device['Socket'].close()

            elif timeout > 0:
                device['Timeout'] = timeout - 1

        except KeyError:
            continue

    scheduler.enter(60, 1, checkDeviceAndCPConnection, (scheduler,))


# /**************************** MAIN *******************************/


#IrdServerAddressIp = '10.3.212.46'
#IrdGatewayAddress = '10.3.10.1'
#IrdMaskAddress = '255.255.0.0'
#IrdServerPort = 3041



print(TITLE_COLOR)
text = APP_NAME + " - " + VERSION + ", by "+ AUTHOR + ", " + DATE
print(text)
print(STANDARD_COLOR)

AddressServer = (IrdServerAddressIp, IrdServerPort)
Server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    Server.bind(AddressServer)
    Server.listen(5)

    # Mode CLIENT: Attente de connection
    print("..... Waiting for connections .....")

    # Gestion du timout de connexion
    ConnectionSpyThread = threading.Thread(target=ConnectionSpy)
    ConnectionSpyThread.start()

    while 1:
        (ConnectedSocket, AddressClient) = Server.accept()

        requestedConnectionThread = threading.Thread(target=readParseRequestFromClient,
                                                 args=(ConnectedSocket, AddressClient,))
        requestedConnectionThread.start()

except OSError:
    print('ERROR: Cannot bind socket')

# /************************** END MAIN *****************************/

