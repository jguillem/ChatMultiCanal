# Example TCP socket client that connects to a server that upper cases text
import sys
from socket import *
import threading
import select
import pickle
import sys

sentence = ""
class client(threading.Thread):

    def __init__(self):
        # Default to running on localhost, port 12000
        self.serverName = '192.168.1.134'
        self.serverPort = 12000
        self.sala_activa = ""
        self.alias = ""
        self.msg_server = ""

    # Metodo encargado del establecimiento de la conexion
    def connexion(self):
        # Optional server name argument
        if (len(sys.argv) > 1):
            self.serverName = sys.argv[1]

        # Optional server port number
        if (len(sys.argv) > 2):
            self.serverPort = int(sys.argv[2])

        # Request IPv4 and TCP communication
        self.clientSocket = socket(AF_INET, SOCK_STREAM)

        # Open the TCP connection to the server at the specified port
        self.clientSocket.connect((self.serverName,self.serverPort))

        # Una vez establecida la conexion, la primera respuesta del servidor
        # es el listado de alias ya conectados
        # Esta informacion servira para ayudar el usuario a no poner un alias repetido
        llistat_alias = self.recibir_mensaje()
        print "Usuaris connectats: "
        print llistat_alias

        # Introducion del alias por parte del usuario
        alias = raw_input('Introdueix el alias: ')
        self.enviar_mensaje(alias)
        respuesta = self.recibir_mensaje()

        while respuesta == "alias_repetit":

            # Se solicita al usuario el alias
            alias = raw_input('Alias repetit intro altre alias: ')
            self.enviar_mensaje(alias)
            respuesta = self.recibir_mensaje()

        self.alias = alias



    def enviar_mensaje(self,sentence):
        self.clientSocket.send(sentence)

    def recibir_mensaje_daemon(self):
        self.enviar_mensaje("read_to_listen")
        msg_rebut = ""
        while msg_rebut != "bye":
            msg_rebut = pickle.loads(self.clientSocket.recv(2048))
            objClient.set_msg_server(msg_rebut)

            if msg_rebut == "alias":
                objClient.sala_activa = ""

            if type(msg_rebut) and msg_rebut != "ok" and msg_rebut != "alias":
                if msg_rebut !=[]:
                    sys.stdout.write("\r\x1b[K"+'                                                                           '+'\r')

                    if msg_rebut == "listas":
                        todas = pickle.loads(self.clientSocket.recv(2048))
                        lista_privada = todas[0]
                        lista_invitada = todas[1]
                        lista_own = todas[2]
                        salas_servidor = todas[3]
                        print "Sales Privades: ",
                        print lista_privada
                        print "Sales Visitant: ",
                        print lista_invitada
                        print "Sales Propies: ",
                        print lista_own
                        print "Altres Sales: ",
                        print salas_servidor

                    elif msg_rebut == "privada":
                        objClient.sala_activa = pickle.loads(self.clientSocket.recv(2048))

                    elif msg_rebut == "users":
                        if objClient.sala_activa == "":
                            print "server@!!!>No tens cap sala activa"
                        else:
                            msg_rebut = pickle.loads(self.clientSocket.recv(2048))
                            #print "server@>Usuaris en " + objClient.sala_activa,
                            print msg_rebut

                    else:
                        print msg_rebut


                    sys.stdout.write('\r')
                    sys.stdout.write("\x1b[K" + objClient.sala_activa + "@" + objClient.alias + '>')
                    sys.stdout.write('\r')
                    sys.stdout.flush()
            elif msg_rebut != "ok" and msg_rebut != "alias":

                sys.stdout.write("\r\x1b[K"+'                                                                            '+'\r')

                if msg_rebut == "listas":
                    todas = pickle.loads(self.clientSocket.recv(2048))
                    lista_privada = todas[0]
                    lista_invitada = todas[1]
                    lista_own = todas[2]
                    salas_servidor = todas[3]
                    print "Sales Privades: ",
                    print lista_privada
                    print "Sales Visitant: ",
                    print lista_invitada
                    print "Sales Propies: ",
                    print lista_own
                    print "Altres Sales: ",
                    print salas_servidor

                elif msg_rebut == "privada":
                    objClient.sala_activa = pickle.loads(self.clientSocket.recv(2048))
                else:
                    print msg_rebut

                sys.stdout.write('\r')
                sys.stdout.write("\x1b[K" + objClient.sala_activa + "@" + objClient.alias + '>')
                sys.stdout.write('\r')
                sys.stdout.flush()

    def recibir_mensaje(self):
        msg_rebut = ""
        while msg_rebut == "":
            msg_rebut = pickle.loads(self.clientSocket.recv(2048))


        return msg_rebut

    def tratar_comando(self, sentence):
        cmd = ""
        sala = ""
        if len(sentence.split(" ",1)) > 1:
            cmd = sentence.split(" ",1)[0]
            sala = sentence.split(" ",1)[1]
        elif len(sentence.split(" ",1)) == 1:
            cmd = sentence.split(" ",1)[0]

        return (cmd,sala)

    def set_msg_server(self,sentence):
        self.msg_server = sentence

    def get_msg_server(self):
        return self.msg_server

if __name__ == '__main__':

    # Declaracion del objeto cliente y establecimiento de la conexion
    objClient = client()
    objClient.connexion()

    # Si la conexion se ha establecido recibimos mensaje positivo
    print 'Benvingut al servidor, usuari ' + objClient.alias
    threading.Thread(target=objClient.recibir_mensaje_daemon,args=(sentence)).start()

    # Mientra no haya peticion de desconexion
    while sentence != "desconectando":
        if objClient.get_msg_server() == "ok" or objClient.get_msg_server() == "" or objClient.get_msg_server() == "alias":
            sentence = raw_input("\x1b[K" + objClient.sala_activa + "@" + objClient.alias + '>')
        else:
            sentence = raw_input()
        cmd = ""
        sala = ""

        cmd,sala = objClient.tratar_comando(sentence)

        if cmd == "/bye":
            sortir = False
            while not sortir:
                r = raw_input('Desitges sortir (si/no)?')
                if r == "si":
                    objClient.enviar_mensaje(sentence)
                    sentence = "desconectando"
                    sortir = True
                if r == "no":
                    sortir = True

                elif r != "no" and r != "si":
                    print 'si o no \n'
        elif cmd == "/cs":
            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            else:
                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

                while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break

                if objClient.get_msg_server() == "ok":
                    objClient.sala_activa = sala

        elif cmd == "/us":

            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            else:
                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

            while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break

            if objClient.get_msg_server() == "ok":
                objClient.sala_activa = sala


        elif cmd == "/ds":
            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            else:
                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

                while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break
                if (objClient.get_msg_server() == "ok" or objClient.get_msg_server() == "alias") and objClient.sala_activa == sala:
                    print "server@!!!>Has deixat la sala " + sala
                    print "server@!!!>Cap sala activa. Uneix-te a una sala (/us) o canvia sala activa (/sa)"
                    if objClient.get_msg_server() == "alias":
                        objClient.sala_activa = ""

        elif cmd == "/sa":
            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            elif sala == objClient.sala_activa:
                print "server@!!!>Ja et trobes dins de la sala" + sala
            else:
                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

                while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break

                if objClient.get_msg_server() == "ok":
                    print "server@!!!>Has entrat a la sala " + sala
                    objClient.sala_activa = sala
        elif cmd == "/es":
            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            else:
                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

                while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break
                if objClient.get_msg_server() == "ok":
                    print "server@!!!>Has eliminat la sala " + sala
                    #if objClient.sala_activa == sala:
                        #objClient.sala_activa = ""

        elif cmd == "/cp":

            if sala == "":
                print "server@!!!>Introdueix un nom per la sala"
            else:

                objClient.set_msg_server("")
                objClient.enviar_mensaje(sentence)

                while objClient.get_msg_server() == "":
                    if objClient.get_msg_server() != "":
                        break
        elif cmd == "/help":
            print "/cs nom_sala -> Crea una sala"
            print "/us nom_sala -> Unir-se a una sala"
            print "/ls          -> Llista de sales"
            print "/cp usuari   -> Crear sala privada amb usuari"
            print "/es nom_sala -> Eliminar una sala"
            print "/ds nom_sala -> Sortir duna sala"
            print "/lu          -> Llistat d'usuaris de la sala on ens trobem"
            print "/bye         -> Sortir del Chat"
            print "/help        -> Mostra informacio dajuda"

        else:
            objClient.set_msg_server("")
            objClient.enviar_mensaje(sentence)

    objClient.clientSocket.close()
    print "Desconectat"