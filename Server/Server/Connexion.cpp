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
            int poll_c = poll(this->_fds.data(), _fds.size(), 0);
            if (poll_c < 0 && this->_serverRun != RunningState::STOP)
                throw zappy::error::ServerConnection("Poll failed");
        }

        for (auto &pfd: this->_fds) {
            if (pfd.revents & POLLIN) {
                {
                    std::lock_guard<std::mutex> lock(this->_socketLock);
                    if (pfd.fd == this->_socket->getSocket()) {
                        this->_fds.push_back(this->_socket->acceptConnection());
                        continue;
                    }
                }
                char buffer[1024] = {0};
                int bytesRead = read(pfd.fd, buffer, sizeof(buffer));
                std::string content(buffer);
                content.erase(content.find_last_not_of(" \n\r\t") + 1);

                if (bytesRead <= 0 || content.compare("exit") == 0) {
                    std::cout << "Client disconnected: " << pfd.fd
                              << std::endl;
                    this->_clients.erase(pfd.fd);
                    this->_game->removeFromTeam(pfd.fd);
                    ::close(pfd.fd);
                    break;
                }

                for (const auto &team : this->_game->getTeamList()) {
                    if (content.compare(team.getName()) == 0) {
                        bool hasJoin = this->_game->handleTeamJoin(pfd.fd, team.getName());
                        if (hasJoin) {
                            this->_socket->sendMessage(pfd.fd, team.getName());
                            break;
                        }
                        this->_socket->sendMessage(pfd.fd, "Invalid team");
                        break;
                    } else
                        handleClientMessage(pfd.fd, content);
                }
            }
        }
    }
}
