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
    auto itClient = this->_users.find(clientSocket);
    if (itClient == _users.end() ||
        itClient->second.getState() != zappy::server::ClientState::CONNECTED)
        return;

    std::lock_guard<std::mutex> lock(*(itClient->second.queueMutex));
    itClient->second.queueMessage.push(buffer);
}

void zappy::server::Server::handleTeamJoin(
    int clientSocket, const std::string &teamName)
{

    auto itClient = _users.find(clientSocket);
    if (itClient != _users.end() &&
        itClient->second.getState() == zappy::server::ClientState::CONNECTED) {
        this->_socket->sendMessage(clientSocket, "Already in a team\n");
        return;
    }

    auto it = std::find_if(_teamList.begin(), _teamList.end(),
        [&teamName](const zappy::game::Team &team) {
            return team.getName() == teamName;
        });

    if (it == _teamList.end()) {
        this->_socket->sendMessage(clientSocket, "ko\n");
        return;
    }

    if (it->getPlayerList().size() >= static_cast<std::size_t>(_clientNb)) {
        this->_socket->sendMessage(clientSocket, "ko\n");
        return;
    }
    zappy::server::Client user(clientSocket);
    zappy::game::Player newPlayer(user);
    user.setState(zappy::server::ClientState::CONNECTED);

    _users.emplace(clientSocket, user);
    it->addPlayer(newPlayer);

    std::string msg =
        std::to_string(_clientNb - it->getPlayerList().size()) + "\n";

    this->_socket->sendMessage(clientSocket, msg.c_str());
    msg = std::to_string(_width) + " " + std::to_string(_height) + "\n";
    this->_socket->sendMessage(clientSocket, msg.c_str());
    std::cout << "Client " << clientSocket << " joined team " << teamName
              << std::endl;
}

void disconnectClient() {}

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
                    _users.erase(_fds[i].fd);
                    _fds.erase(_fds.begin() + i);
                    --i;
                    continue;
                }

                for (auto team : this->_teamList) {
                    if (content.compare(team.getName()) == 0) {
                        handleTeamJoin(_fds[i].fd, team.getName());
                        break;
                    } else
                        handleClientMessage(_fds[i].fd, content);
                }
            }
        }
    }
}
