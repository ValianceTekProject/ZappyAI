/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp"
#include "Server.hpp"
#include "ServerPlayer.hpp"
#include <algorithm>
#include <thread>

const constexpr int nbOrientation = 4;

void zappy::game::Game::messageToGUI(const std::string &msg)
{
    for (auto &team : this->getTeamList()) {
        if (team->getName() == "GRAPHIC") {
            for (auto &player : team->getPlayerList()) {
                if (player)
                    player->getClient().sendMessage(msg);
            }
        }
    }
}

void zappy::game::Game::_addPlayerToTeam(
    std::shared_ptr<zappy::game::ITeams> team, int clientSocket)
{
    std::srand(std::time({}));
    int randVal = std::rand() % nbOrientation;
    zappy::game::Orientation orientation =
        static_cast<zappy::game::Orientation>(randVal);
    zappy::server::Client user(clientSocket);
    zappy::game::Egg egg = this->_map.popEgg();
    user.setState(zappy::server::ClientState::CONNECTED);
    auto newPlayer = std::make_shared<zappy::game::ServerPlayer>(
        std::move(user), _idPlayerTot, egg.x, egg.y, orientation, *team, 1);
    newPlayer->teamName = team->getName();
    this->_idPlayerTot += 1;
    team->addPlayer(newPlayer);
    this->_playerList.push_back(newPlayer);
    if (auto lastPlayer = this->_playerList.back().lock(); lastPlayer) {
        std::cout << "Team name = '" << lastPlayer->teamName << "'" << std::endl;
        if (lastPlayer->teamName != "GRAPHIC") {
            std::ostringstream orientationStream;
            orientationStream << lastPlayer->orientation;
            this->messageToGUI(std::string("pnw " + std::to_string(this->_idPlayerTot) + " "
                + std::to_string(lastPlayer->x) + " " + std::to_string(lastPlayer->y) + " "
                + orientationStream.str() + " " + std::to_string(lastPlayer->level) + " "
                + lastPlayer->teamName + "\n"));
        }
    }
}

bool zappy::game::Game::_checkAlreadyInTeam(int clientSocket)
{
    for (const auto &team : this->_teamList) {
        for (const auto &player : team->getPlayerList()) {
            const auto &socket = player->getClient();
            if (socket.getSocket() == clientSocket) {
                return true;
            }
        }
    }
    return false;
}

bool zappy::game::Game::handleTeamJoin(
    int clientSocket, const std::string &teamName)
{
    auto it = std::find_if(this->_teamList.begin(), this->_teamList.end(),
        [&teamName](const std::shared_ptr<zappy::game::ITeams> (team)) {
            return team->getName() == teamName;
        });

    auto itPlayerTeam = std::dynamic_pointer_cast<TeamsPlayer>(*it);
    if (itPlayerTeam) {
        if (it == this->_teamList.end() ||
            static_cast<int>(itPlayerTeam->getPlayerList().size()) >= itPlayerTeam->getClientNb()) {
            return false;
        }
    }

    if (this->_checkAlreadyInTeam(clientSocket) == true)
        return false;

    this->_addPlayerToTeam(*it, clientSocket);
    return true;
}

void zappy::game::Game::removeFromTeam(int clientSocket)
{
    for (size_t i = 0; i < this->_teamList.size(); i += 1) {
        auto &team = this->_teamList[i];
        for (auto &player : team->getPlayerList()) {
            if (player->getClient().getSocket() == clientSocket) {
                team->removePlayer(clientSocket);
                return;
            }
        }
    }
}

void zappy::game::Game::runGame()
{
    this->_isRunning = RunningState::RUN;
    auto lastUpdate = std::chrono::steady_clock::now();

    while (this->_isRunning != RunningState::STOP) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - lastUpdate);
        for (auto &team : this->getTeamList()) {
            for (auto &player : team->getPlayerList()) {
                if (!player->getClient().queueMessage.empty()) {
                    if (player->teamName.compare("GRAPHIC")) {
                        this->_commandHandlerGui.processClientInput(
                            player->getClient().queueMessage.front(), *player);
                        player->getClient().queueMessage.pop();
                    } else
                        this->_commandHandler.processClientInput(
                            player->getClient().queueMessage.front(), *player);
                }
            }
        }
        if (elapsed >= static_cast<std::chrono::seconds>(this->_baseFreqMs)) {
            this->_playTurn();
            lastUpdate = now;
            continue;
        }
        std::this_thread::sleep_for(
            std::chrono::milliseconds(1));  // temporaire
    }
}
