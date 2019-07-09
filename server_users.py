#usr/bin/env python3

import socket
import sys
import pickle
import select
import os

#PROTOCOL MSGs
P2P_CHAT_PY_PROTOCOL_HI = 'ChatPy_Hi'
P2P_CHAT_PY_PROTOCOL_HI_ACK = 'ChatPy_Hi_Ack'
P2P_CHAT_PY_PROTOCOL_BYE = 'ChatPy_Bye'
P2P_CHAT_PY_PROTOCOL_BYE_ACK = 'ChatPy_Bye_Ack'
P2P_CHAT_PY_PROTOCOL_UPDATE = 'ChatPy_Update'
P2P_CHAT_PY_PROTOCOL_UPDATE_ACK = 'ChatPy_Update_Ack'
P2P_CHAT_PY_PROTOCOL_CONN = 'ChatPy_Conn'
P2P_CHAT_PY_PROTOCOL_CONN_ACK = 'ChatPy_Conn_Ack'
P2P_CHAT_PY_PROTOCOL_DIS = 'ChatPy_Dis'
P2P_CHAT_PY_PROTOCOL_DIS_ACK = 'ChatPy_Dis_Ack'
P2P_CHAT_PY_PROTOCOL_MSG = 'ChatPy_Msg'


#To print all clients connected
def print_conn(sock_addr_port):
    
    os.system('clear')
    for clients in sock_addr_port:
        print('Client: ' + str(clients[1]) + '| Port: '+str(clients[2]))

#To remove from list when some client goes out 
def remove_client_from_list(sock_addr_port,sock_to_remove):

    for clients in sock_addr_port:
        if clients[0] is sock_to_remove:
            sock_addr_port.remove(clients)

def getIpFromSocket(sock_addr_port,sock_to_rcv):

    for clients in sock_addr_port:
        if clients[0] is sock_to_rcv:
            return clients[1]

if __name__ == "__main__":
    #Check argv's
    if len(sys.argv) < 2:
        print('Error: usage: ./' + sys.argv[0] + ' <Port>')
        exit()
    else:

        port = int(sys.argv[1])        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setblocking(0)
        s.bind(('',port))
        s.listen(5)

        #Sockets to read
        sockets_rd = [s]

        #Just for track all conn
        sock_addr_port = []

        #Peer list 
        peer_list = []
        id_peer = 1

        while True:
            try:
                events_rd,events_wr,events_excp = select.select( sockets_rd,[],[])
            except KeyboardInterrupt:
                print('\n\n\nShutdown....')
                for sock in sockets_rd:
                    sock.close()
                sys.exit(0)

            for event in events_rd:

                if event == s:
                    #Add user into peers list 
                    conn, addr = s.accept()
                    sock_addr_port.append([conn,addr[0],addr[1]])
                    conn.setblocking(0)
                    sockets_rd.append(conn)
                else:
                    #Handle other conn
                    for sock_to_rcv in sockets_rd:
                        if sock_to_rcv != s and sock_to_rcv is event:
                            data = pickle.loads(sock_to_rcv.recv(4096))
                            if data:
                                if data[0] == P2P_CHAT_PY_PROTOCOL_HI:

                                    #First add him to peer list
                                    data[1].append(getIpFromSocket(sock_addr_port,sock_to_rcv))
                                    data[1].append(id_peer)
                                    peer_list.append(data[1])
                                    

                                    #Second send him peer list 
                                    sock_to_rcv.sendall(pickle.dumps([P2P_CHAT_PY_PROTOCOL_HI_ACK,peer_list,id_peer]))

                                    id_peer += 1
                                    
                                elif data[0] == P2P_CHAT_PY_PROTOCOL_BYE:
                                    
                                    #First remove the peer from the peer list 
                                    data[1].append(getIpFromSocket(sock_addr_port,sock_to_rcv))
                                    data[1].append(data[2])
                                    peer_list.remove(data[1])

                                    #Second send to him bye_ack
                                    sock_to_rcv.sendall(pickle.dumps([P2P_CHAT_PY_PROTOCOL_BYE_ACK, data[1]]))
                                    sockets_rd.remove(sock_to_rcv)
                                    remove_client_from_list(sock_addr_port,sock_to_rcv)
                                    

                                elif data[0] == P2P_CHAT_PY_PROTOCOL_UPDATE:

                                    #Just update our peer with the peer list 
                                    sock_to_rcv.sendall(pickle.dumps([P2P_CHAT_PY_PROTOCOL_UPDATE_ACK,peer_list]))
                            else:
                                #Remove one Peer
                                sock_to_rcv.close()
                                sockets_rd.remove(sock_to_rcv)
                                remove_client_from_list(sock_addr_port,sock_to_rcv)
                
                #Print al active conn
                print_conn(sock_addr_port)
            

