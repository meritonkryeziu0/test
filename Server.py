import pickle
import socket
import threading
from typing import Tuple
import rsa
from Cryptodome.Cipher import AES

hostIP = socket.gethostname()    # My local IP adress
port = 5555

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((hostIP,port))

server.listen()

clients=[]
nicknames=[]

server_symetric_key= pickle.dumps("This is the key!")  # Each client will get this key, after it will be encrypted with asymetric encryption

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message= client.recv(1024)
            broadcast(message) # Sends the recieved message to all the other clients
        except:
            index= clients.index(client)
            clients.remove(client)
            client.close()
            nickname=nicknames[index]
            broadcast(aes_encryption(f"{nickname} has Disconnected from the server \n"))
            nicknames.remove(nickname)

def aes_encryption(plain_text)->Tuple:
    cipher = AES.new(pickle.loads(server_symetric_key).encode('utf-8'), AES.MODE_EAX)   # Encrypt the sent message
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(plain_text.encode('utf-8'))
    return pickle.dumps((ciphertext,nonce,tag))  #  The tuple is all the data that is needed for the decryption. It is converted to Bytes to be sent

def main():
    while True:
        client, address= server.accept()

        client.send(pickle.dumps("NICK")) # Asks the user for his nickname, and save it
        nickname = pickle.loads(client.recv(1024))
        nicknames.append(nickname)
        clients.append(client)

        ### Diffie Hellman key exchange method starts HERE ###
        client.send(pickle.dumps("PUBLIC KEY")) # Asks the user for his public encyption key, and save it. This will be used to asymetric encrypt the symetric key

        pickled_client_public_key = client.recv(1024) 

        client_public_key = pickle.loads(pickled_client_public_key)  # Turns the key back to PublicKey object, as RSA moudle requires

        encrypted_symetric_key= rsa.encrypt(server_symetric_key,client_public_key)  # Pass the symetric (encrypted) key to the client
        client.send(encrypted_symetric_key)
        
        broadcast(aes_encryption(f"{nickname} has connected to the server \n")) # Send the encrypted welcome message to all the connected users 

        thread= threading.Thread(target=handle, args=(client,))
        thread.start()


print("server is running...")
main()
