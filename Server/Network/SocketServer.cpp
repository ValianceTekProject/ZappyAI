//
// EPITECH PROJECT, 2025
// Socket
// File description:
// Socket
//

#include "SocketServer.hpp"
#include <arpa/inet.h>
#include <cstring>
#include <iostream>
#include <memory>
#include <netinet/in.h>
#include <string>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

zappy::server::SocketServer::SocketServer(int port, std::uint8_t nbClients)
{
    this->_port = port;
    this->_nbClients = nbClients;
    if (this->_port <= 0)
        throw error::SocketError("Wrong Port for socket");

    this->_address = std::make_unique<struct sockaddr_in>();
    if (this->_address == nullptr)
        throw error::SocketError("Unable to init sockaddr");

    this->_address->sin_addr.s_addr = INADDR_ANY;
    this->_address->sin_port = htons(this->_port);
    this->_address->sin_family = AF_INET;

    this->_initSocket();
}

void zappy::server::SocketServer::_initSocket()
{
    this->_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (this->_socket < 0)
        throw error::SocketError("Socket failed");

    if (bind(this->_socket, (struct sockaddr *)this->_address.get(),
            sizeof(struct sockaddr_in)) < 0) {
        if (errno == EADDRINUSE)
            throw error::SocketError("Port already used");
        throw error::SocketError("Bind failed");
    }

    if (listen(this->_socket, this->_nbClients) < 0)
        throw error::SocketError("Listen failed");
}

zappy::server::SocketServer::~SocketServer()
{
    if (this->_socket > 0) {
        close(this->_socket);
    }
}

void zappy::server::SocketServer::createConnection()
{
    if (connect(this->_socket,
            reinterpret_cast<sockaddr *>(this->_address.get()),
            this->_addrlen) == -1) {
        throw error::SocketError("Connect Failed");
    }
}

void zappy::server::SocketServer::sendMessage(
    int clientSocket, const std::string &msg) const
{
    std::string messageFormat = msg + "\n";
    if (send(clientSocket, messageFormat.c_str(),
            strlen(messageFormat.c_str()), 0) == -1) {
        throw error::SocketError("Send Failed " + msg);
    }
}

int zappy::server::SocketServer::getSocket() const
{
    return this->_socket;
}

std::string zappy::server::SocketServer::getServerInformation()
{
    constexpr short buffSize = 256;

    char buf[buffSize];
    std::string str;
    ssize_t bytes_read = 0;

    while (true) {
        bytes_read = read(this->_socket, buf, sizeof(buf));
        if (bytes_read < 0)
            break;
        if (bytes_read == 0) {
            close(this->_socket);
            this->_socket = invalidSocket;
            throw error::SocketError("Server disconnected");
        }
        str.append(buf, bytes_read);
        if (bytes_read < buffSize)
            break;
    }
    std::cout << str << std::endl;
    return str;
}

void zappy::server::SocketServer::getData(std::vector<struct pollfd> &fds) const
{
    int poll_c = poll(fds.data(), fds.size(), 0);
    if (poll_c < 0)
        throw error::SocketError("Poll failed");
}

pollfd zappy::server::SocketServer::acceptConnection()
{
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);
    int clientSocket =
        accept(this->_socket, (sockaddr *)&clientAddr, &clientLen);

    if (clientSocket < 0)
        throw error::SocketError("Accept failed");

    pollfd fd = {clientSocket, POLLIN, 0};

    this->sendMessage(clientSocket, "WELCOME\n");
    return fd;
}
