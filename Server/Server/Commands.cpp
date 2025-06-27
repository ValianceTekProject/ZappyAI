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
                auto teamsGui = std::dynamic_pointer_cast<zappy::game::TeamsGui>(team);
                if (teamsGui) {
                    this->_game->getCommandHandlerGui().handleMsz(*teamsGui->getPlayerList().back());
                    this->_game->getCommandHandlerGui().handleSgt(*teamsGui->getPlayerList().back());
                    this->_game->getCommandHandlerGui().handleMct(*teamsGui->getPlayerList().back());
                    this->_game->getCommandHandlerGui().handleTna(*teamsGui->getPlayerList().back());
                    this->_game->getCommandHandlerGui().handlePnw(*teamsGui->getPlayerList().back());
                    for (auto &teams : this->_game->getTeamList()) {
                        if (teams->getName() != "GRAPHIC") {
                            for (auto &players : teams->getPlayerList()) {
                                this->_game->getCommandHandlerGui().handlePin(*teamsGui->getPlayerList().back(),
                                    std::to_string(players->getId()));
                                this->_game->getCommandHandlerGui().handlePlv(*teamsGui->getPlayerList().back(),
                                    std::to_string(players->getId()));
                            }
                        }
                    }
                    for (auto &eggs : this->_game->getMap().getEggList())
                        this->_game->getCommandHandler().messageToGUI("enw #" + std::to_string(eggs.getId()) + " -1 " + std::to_string(eggs.x) + " " +
                            std::to_string(eggs.y) + "\n");
                    return;
                }
                return;
            }
            this->_socket->sendMessage(pfd.fd, "Invalid team");
            return;
        }
    }
    handleClientMessage(pfd.fd, command);
}
