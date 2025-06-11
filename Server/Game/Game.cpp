/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp"
#include "Player/ServerPlayer.hpp"
#include "Server.hpp"
#include "Teams/Teams.hpp"
#include <algorithm>
#include <thread>

void zappy::game::Game::_addPlayerToTeam(
    zappy::game::Team &team, int clientSocket)
{
    zappy::server::Client user(clientSocket);
    std::unique_ptr<zappy::game::ServerPlayer> newPlayer =
        std::make_unique<zappy::game::ServerPlayer>(std::move(user), _idTot, 0, 0, zappy::game::Orientation::NORTH, 1);
    _idTot += 1;
    user.setState(zappy::server::ClientState::CONNECTED);

    team.addPlayer(std::move(newPlayer));
}

bool zappy::game::Game::_checkAlreadyInTeam(int clientSocket)
{
    for (const auto &team : this->_teamList) {
        for (const auto &player : team.getPlayerList()) {
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
        [&teamName](const zappy::game::Team &team) {
            return team.getName() == teamName;
        });

    if (it == this->_teamList.end() || static_cast<int> (it->getPlayerList().size()) >= this->_clientNb)
        return false;

    if (this->_checkAlreadyInTeam(clientSocket) == true)
        return false;
    this->_addPlayerToTeam(*it, clientSocket);
    return true;
}

void zappy::game::Game::removeFromTeam(int clientSocket)
{
    std::cout << "Trying to remove: " << clientSocket << std::endl;
    for (auto &team: this->_teamList) {
        for (auto &player: team.getPlayerList()) {
            std::cout << "Player: " << player->getClient().getSocket() << std::endl;
            if (player->getClient().getSocket() == clientSocket) {
                std::cout << "Player: " << clientSocket << " removed" << std::endl;
                team.removePlayer(clientSocket);
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
            for (auto &player : team.getPlayerList()) {
                if (!player->getClient().queueMessage.empty()) {
                    this->_commandHandler.processClientInput(player->getClient().queueMessage.front(), *player);
                    player->getClient().queueMessage.pop();
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
