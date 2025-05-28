/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ClientConnexion
*/

#include "Server.hpp"

std::function<void(int)> zappy::Server::takeSignal;

void zappy::Server::closeClients()
{
    // TODO send message to stop connexion with clients and AI
    _teamList.clear();
}

void zappy::Server::stopServer(int sig)
{
    std::cout << "Received signal " << sig << ". Closing server in progress..." << std::endl;
    _serverRun = false;
    closeClients();
    close(_servSocket);
}

void zappy::Server::signalWrapper(int sig)
{
    if (takeSignal)
        takeSignal(sig);
}

void zappy::Server::handleNewConnection()
{
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);
    int clientSocket = my_accept(_servSocket, (sockaddr *)&clientAddr, &clientLen);

    if (clientSocket < 0)
        throw zappy::error::ServerConnection("Accept failed");

    std::cout << "New connection: " << clientSocket << std::endl;
    fds.push_back({clientSocket, POLLIN, 0});

    sendMessage(clientSocket, "WELCOME\n");
}

void zappy::Server::handleTeamJoin(int clientSocket, const std::string &teamName)
{

    auto itUser = _users.find(clientSocket);
    if (itUser != _users.end() && itUser->second.getState() == zappy::server::ClientState::CONNECTED) {
        sendMessage(clientSocket, "Already in a team\n");
        return;
    }

    auto it = std::find_if(_teamList.begin(), _teamList.end(),
        [&teamName](const zappy::game::Team &team) {
            return team.getName() == teamName;
        });

    if (it == _teamList.end()) {
        sendMessage(clientSocket, "ko\n");
        return;
    }

    if (it->getPlayerList().size() >= static_cast<std::size_t>(_clientNb)) {
        sendMessage(clientSocket, "ko\n");
        return;
    }
    zappy::server::User user(clientSocket);
    zappy::game::Player newPlayer(user);
    user.setState(zappy::server::ClientState::CONNECTED);

    _users.emplace(clientSocket, user);
    it->addPlayer(newPlayer);

    std::string msg = std::to_string(_clientNb - it->getPlayerList().size()) + "\n";

    sendMessage(clientSocket, msg.c_str());
    msg = std::to_string(_width) + " " + std::to_string(_height) + "\n";
    sendMessage(clientSocket, msg.c_str());
    std::cout << "Client " << clientSocket << " joined team " << teamName << std::endl;
}

void zappy::Server::serverLoop()
{
    takeSignal = std::bind(&zappy::Server::stopServer, this, std::placeholders::_1);
    my_signal(SIGINT, signalWrapper);
    while (_serverRun) {
        int poll_c = my_poll(fds.data(), fds.size(), 10);
        if (poll_c < 0 && _serverRun)
            throw zappy::error::ServerConnection("Poll failed");

        for (std::size_t i = 0; i < fds.size(); i++) {
            if (fds[i].revents & POLLIN) {
                if (fds[i].fd == _servSocket)
                    handleNewConnection();
                else {
                    char buffer[1024] = {0};
                    int bytesRead = read(fds[i].fd, buffer, sizeof(buffer));
                    std::string content(buffer);
                    content.erase(content.find_last_not_of(" \n\r\t") + 1);

                    if (bytesRead <= 0 || content.compare("exit") == 0) {
                        std::cout << "Client disconnected: " << fds[i].fd << std::endl;
                        close(fds[i].fd);
                        _users.erase(fds[i].fd);
                        fds.erase(fds.begin() + i);
                        --i;
                        continue;
                    }

                    for (auto team : _teamList) {
                        if (content.compare(team.getName()) == 0)
                            handleTeamJoin(fds[i].fd, team.getName());
                    }
                }
            }
        }
    }
}