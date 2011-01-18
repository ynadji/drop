import socket

def gateway():
    """Guest's gateway address."""
    return slash24prefix() + '.1'

def guestip():
    """Not platform independent, but works on my setup with Windows."""
    return socket.gethostbyname(socket.gethostname())

def vmnumber():
    """VM number is denoted by the third octet."""
    octets = guestip().split('.')
    return octets[2]

def slash24prefix():
    """If guestip() is '192.168.1.41', return '192.168.1'."""
    octets = guestip().split('.')
    return '.'.join(octets[:3])
