/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp"
#include "Player/Player.hpp"
#include "Server.hpp"
#include <algorithm>
#include <thread>

bool zappy::game::Game::handleTeamJoin(
    int clientSocket, const std::string &teamName)
{
    auto it = std::find_if(this->_teamList.begin(), this->_teamList.end(),
        [&teamName](const zappy::game::Team &team) {
            return team.getName() == teamName;
        });

    if (it == this->_teamList.end()) {
        return false;
    }

    for (const auto &team: this->_teamList) {
        for (const auto &player: team.getPlayerList()) {
            const auto &socket = player->getClient();
            std::cout << "Socket: " << clientSocket << std::endl;
            std::cout << "Client: " << socket.getSocket() << std::endl;
            if (socket.getSocket() == clientSocket) {
                std::cout << "Déjà dans une équipe" << std::endl;
                return false;
            }
        }
    }

    zappy::server::Client user(clientSocket);
    std::unique_ptr<zappy::game::ServerPlayer> newPlayer = std::make_unique<zappy::game::ServerPlayer>(std::move(user));
    std::cout << "Name: " << clientSocket << " " << newPlayer->getClient().getSocket() << std::endl;
    user.setState(zappy::server::ClientState::CONNECTED);

    it->addPlayer(std::move(newPlayer));
    return true;
}

void zappy::game::Game::runGame()
{
    this->_isRunning = RunningState::RUN;
    auto lastUpdate = std::chrono::steady_clock::now();

    while (this->_isRunning != RunningState::STOP) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - lastUpdate);

        if (elapsed >= this->_baseFreqMs) {
            this->_playTurn();
            lastUpdate = now;
            continue;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1)); // temporaire
    }
}

