//
// EPITECH PROJECT, 2025
// Socket
// File description:
// Socket
//

#include "Socket.hpp"
#include <arpa/inet.h>
#include <cstring>
#include <iostream>
#include <memory>
#include <netinet/in.h>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

zappy::server::Socket::Socket(int port, std::uint8_t nbClients)
{
    this->_port = port;
    this->_nbClients = nbClients;
    this->_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (this->_socket < 0)
        throw SocketError("Socket failed");
    if (this->_port <= 0)
        throw SocketError("Wrong Port for socket");

    this->_address = std::make_unique<struct sockaddr_in>();
    if (this->_address == nullptr)
        throw SocketError("Unable to init sockaddr");

    this->_address->sin_addr.s_addr = INADDR_ANY;
    this->_address->sin_port = htons(this->_port);
    this->_address->sin_family = AF_INET;

    std::cout << "Port: " << port << std::endl;
    std::cout << "Socket: " << this->_socket << std::endl;
    if (bind(this->_socket, (struct sockaddr *)this->_address.get(),
            sizeof(struct sockaddr_in)) < 0) {
        if (errno == EADDRINUSE)
            throw SocketError("Port already used");
        throw SocketError("Bind failed");
    }
    if (listen(this->_socket, nbClients) < 0)
        throw SocketError("Listen failed");
}

zappy::server::Socket::~Socket()
{
    if (this->_socket > 0) {
        close(this->_socket);
    }
}

void zappy::server::Socket::createConnection()
{
    if (connect(this->_socket,
            reinterpret_cast<sockaddr *>(this->_address.get()),
            this->_addrlen) == -1) {
        throw SocketError("Connect Failed");
    }
}

void zappy::server::Socket::sendMessage(int clientSocket, const std::string &msg) const
{
    std::string messageFormat = msg + "\n";
    if (send(clientSocket, messageFormat.c_str(),
            strlen(messageFormat.c_str()), 0) == -1) {
        throw SocketError("Send Failed");
    }
}

int zappy::server::Socket::getSocket() const
{
    return this->_socket;
}

std::string zappy::server::Socket::getServerInformation()
{
    char buf[256];
    std::string str;
    ssize_t bytes_read = 0;

    while (true) {
        bytes_read = read(this->_socket, buf, sizeof(buf));
        if (bytes_read < 0)
            break;
        if (bytes_read == 0) {
            close(this->_socket);
            this->_socket = -1;
            throw SocketError("Server disconected");
        }
        str.append(buf, bytes_read);
        if (bytes_read < 256)
            break;
    }
    return str;
}

pollfd zappy::server::Socket::acceptConnection()
{
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);
    int clientSocket = accept(this->_socket, (sockaddr *)&clientAddr, &clientLen);

    if (clientSocket < 0)
        throw SocketError("Accept failed");

    std::cout << "New connection: " << clientSocket << std::endl;
    pollfd fd = {clientSocket, POLLIN, 0};

    this->sendMessage(clientSocket, "WELCOME\n");
    return fd;
}

