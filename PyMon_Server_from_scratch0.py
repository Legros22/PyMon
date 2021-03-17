#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Philippe
#
# Created:     16/03/2021
# Copyright:   (c) Philippe 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import socket
#ADRESSE = '127.0.0.0'
ADRESSE = '192.168.1.52'
PORT = 6789

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    serveur.bind((ADRESSE, PORT))
    restart_serveur = 1

    while restart_serveur: #Loop on starting connexion
        serveur.listen(1)
        client, adresseClient = serveur.accept()
        print ('Connexion de ', adresseClient)

        while 1: #loop on message received
            donnees = client.recv(1024)
            if not donnees:
                print ('Erreur de reception.')
                break #sortie du while
            else:
                #convert the "byte" received to a string
                DonneesStr = donnees.decode('UTF-8')
                DonneesStr = DonneesStr.replace("\n","") # supress \n for start of line
                DonneesStr = DonneesStr.replace("\r","") # supress \r for start of line

                #filter received string with just empty string
                #(an empty string always follow a string...)
                if (len(DonneesStr)==0):
                    restart_serveur = 1
                #manage message "END" to stop the server
                elif DonneesStr.upper()=='END':
                    restart_serveur = 0
                    break
                #process other messages
                else:
                    FinReception = 0
                    print ('Reception de:' +DonneesStr+ '  len='+str(len(DonneesStr)))

                    reponse = DonneesStr.upper()+'\n\r'
                    print ('Envoi de :' + reponse)
                    # Response shall be a "byte" list, not char.
                    n = client.send(reponse.encode('UTF-8'))
                    if (n != len(reponse)):
                        print ('Erreur envoi.')
                    else:
                        print ('Envoi ok.')
        print ('Fermeture normale de la connexion avec le client.')
        client.close()
    print ('Arret normal du serveur.')
    serveur.close()

except OSError:
    print ('Fermeture de la connexion avec le client.')
    client.close()
    print ('Arret du serveur.')
    serveur.close()
