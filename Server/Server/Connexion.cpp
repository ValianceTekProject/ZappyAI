/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientConnexion
*/

#include "Client.hpp"
#include "Game.hpp"
#include "Server.hpp"
#include "algorithm"
#include <mutex>

void zappy::server::Server::handleClientMessage(
    int clientSocket, std::string buffer)
{
    std::cout << "Size: " << std::to_string(_clients.size()) << std::endl;
    auto itClient = this->_clients.find(clientSocket);
    if (itClient == this->_clients.end() ||
        itClient->second.getState() != zappy::server::ClientState::CONNECTED) {
            std::cout << "RETURN" << std::endl;
            return;
        }

    std::lock_guard<std::mutex> lock(*(itClient->second.queueMutex));
    std::cout << "AAAAAAAAAAA" << std::endl;
    itClient->second.queueMessage.push(buffer);
}

zappy::server::ClientState zappy::server::Server::_handleClientDisconnection(
    const std::string &content, struct pollfd &pfd)
{
    if (content.empty() || content.compare("exit") == 0) {
        this->_clients.erase(pfd.fd);
        this->_game->removeFromTeam(pfd.fd);
        ::close(pfd.fd);
        return ClientState::DISCONNECTED;
    }
    return ClientState::UNDEFINED;
}

bool zappy::server::Server::_handleNewConnection(struct pollfd &pfd)
{
    std::lock_guard<std::mutex> lock(this->_socketLock);
    if (pfd.fd == this->_socket->getSocket()) {
        pollfd newPollfd = this->_socket->acceptConnection();
        int clientFd = newPollfd.fd;

        this->_clients.emplace(clientFd, zappy::server::Client(clientFd));

        this->_fds.push_back(newPollfd);
        return true;
    }
    return false;
}

void zappy::server::Server::runLoop()
{
    auto signalHandler = std::make_shared<zappy::utils::Signal>(*this, *_game);
    zappy::utils::Signal::initSignalHandling(signalHandler.get());

    while (this->_serverRun == RunningState::RUN) {
        this->_socket->getData(this->_fds);

        for (auto &pfd : this->_fds) {
            if (pfd.revents & POLLIN) {
                if (this->_handleNewConnection(pfd) == true)
                    continue;
                auto content = this->_getClientCommand(pfd);
                if (this->_handleClientDisconnection(content, pfd) ==
                    ClientState::DISCONNECTED)
                    break;
                this->_handleClientCommand(content, pfd);
            }
        }
    }
}
