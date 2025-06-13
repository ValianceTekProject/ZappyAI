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

const constexpr int nbOrientation = 4;

void zappy::game::Game::_addPlayerToTeam(
    zappy::game::Team &team, int clientSocket)
{
    std::srand(std::time({}));
    int randVal = std::rand() % nbOrientation;
    zappy::game::Orientation orientation = static_cast<zappy::game::Orientation>(randVal);
    zappy::server::Client user(clientSocket);
    zappy::game::Egg egg = this->_eggList.front();
    std::cout << "x: " << egg.x << "y: " << egg.y << std::endl;
    this->_eggList.pop();
    user.setState(zappy::server::ClientState::CONNECTED);
    auto newPlayer =
        std::make_shared<zappy::game::ServerPlayer>(std::move(user), _idPlayerTot, egg.x, egg.y, orientation, 1);
    _idPlayerTot += 1;
    team.addPlayer(std::move(newPlayer));
    this->_playerList.push_back(std::move(newPlayer));
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

void zappy::game::Game::setEggsonMap()
{
    for (int i = 0; i < static_cast<int>((_clientNb * _teamList.size())); i += 1) {
        size_t x = std::rand() % _map.getWidth();
        size_t y = std::rand() % _map.getHeight();
        zappy::game::Egg newEgg(_idEggTot, SERVER_FATHER_ID, x, y);
        _idEggTot += 1;
        this->_eggList.push(newEgg);
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
