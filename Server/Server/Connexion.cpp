/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientConnexion
*/

#include "algorithm"
#include "Server.hpp"
#include "Game.hpp"
#include <mutex>

void zappy::server::Server::handleClientMessage(
    int clientSocket, std::string buffer)
{
    auto itClient = this->_clients.find(clientSocket);
    if (itClient ==this->_clients.end() ||
        itClient->second.getState() != zappy::server::ClientState::CONNECTED)
        return;

    std::lock_guard<std::mutex> lock(*(itClient->second.queueMutex));
    itClient->second.queueMessage.push(buffer);
}

void zappy::server::Server::runLoop()
{
    auto signalHandler = std::make_shared<zappy::utils::Signal>(*this, *_game);
    zappy::utils::Signal::initSignalHandling(signalHandler.get());

    while (this->_serverRun == RunningState::RUN) {
        {
            std::lock_guard<std::mutex> lock(this->_socketLock);
            int poll_c = poll(this->_fds.data(), _fds.size(), 100);
            if (poll_c < 0 && this->_serverRun != RunningState::STOP)
                throw zappy::error::ServerConnection("Poll failed");
        }

        for (std::size_t i = 0; i < _fds.size(); i++) {
            if (_fds[i].revents & POLLIN) {
                {
                    std::lock_guard<std::mutex> lock(this->_socketLock);
                    if (_fds[i].fd == this->_socket->getSocket()) {
                        this->_fds.push_back(this->_socket->acceptConnection());
                        continue;
                    }
                }
                char buffer[1024] = {0};
                int bytesRead = read(_fds[i].fd, buffer, sizeof(buffer));
                std::string content(buffer);
                content.erase(content.find_last_not_of(" \n\r\t") + 1);

                if (bytesRead <= 0 || content.compare("exit") == 0) {
                    std::cout << "Client disconnected: " << _fds[i].fd
                              << std::endl;
                    close(_fds[i].fd);
                   this->_clients.erase(_fds[i].fd);
                    _fds.erase(_fds.begin() + i);
                    --i;
                    continue;
                }

                for (const auto &team : this->_game->getTeamList()) {
                    if (content.compare(team.getName()) == 0) {
                        bool hasJoin = this->_game->handleTeamJoin(this->_fds[i].fd, team.getName());
                        std::cout << team.getName() << std::endl;
                        if (hasJoin) {
                            this->_socket->sendMessage(this->_fds[i].fd, team.getName());
                            break;
                        }
                        this->_socket->sendMessage(this->_fds[i].fd, "Invalid team");
                        break;
                    } else
                        handleClientMessage(_fds[i].fd, content);
                }
            }
        }
    }
}
