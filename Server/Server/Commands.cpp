//
// EPITECH PROJECT, 2025
// Commands
// File description:
// Handle commands for server
//

#include "Server.hpp"
#include "my_macros.hpp"

std::string zappy::server::Server::_getClientCommand(const struct pollfd &pfd)
{
    constexpr short buffSize = 1024;

    char buffer[buffSize] = {0};

    read(pfd.fd, buffer, sizeof(buffer));
    std::string content(buffer);
    content.erase(content.find_last_not_of(endSequence) + 1);
    return content;
}

void zappy::server::Server::_handleClientCommand(const std::string &command, struct pollfd &pfd)
{
    for (auto &team : this->_game->getTeamList()) {
        if (command.compare(team->getName()) == 0) {
            bool hasJoin = this->_game->handleTeamJoin(pfd.fd, team->getName());
            if (hasJoin) {
                auto teamsPlayer = std::dynamic_pointer_cast<zappy::game::TeamsPlayer>(team);
                if (teamsPlayer) {
                    std::string msg = std::to_string(teamsPlayer->getClientNb() - teamsPlayer->getPlayerList().size());
                    this->_socket->sendMessage(pfd.fd, msg);
                    msg = std::to_string(this->_width) + " " + std::to_string(this->_height);
                    this->_socket->sendMessage(pfd.fd, msg);
                    return;
                }
            }
            this->_socket->sendMessage(pfd.fd, "Invalid team");
            return;
        }
    }
    handleClientMessage(pfd.fd, command);
}
