/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.cpp
*/

#include "GameState.hpp"

void zappy::game::GameState::updatePlayerPosition(
    const int &id,
    const size_t &x,
    const size_t &y,
    const Orientation &orientation
) {
    Player &player = getPlayerById(id);

    player.x = x;
    player.y = y;
    player.orientation = orientation;
}

void zappy::game::GameState::updatePlayerLevel(const int &id, const size_t &level)
{
    Player &player = getPlayerById(id);

    player.level = level;
}

void zappy::game::GameState::updatePlayerInventory(const int &id, const Inventory &inventory)
{
    Player &player = getPlayerById(id);

    player.setInventory(inventory);
}

void zappy::game::GameState::hatchEgg(const int &eggId)
{
    Egg &egg = getEggById(eggId);
    size_t x = egg.x;
    size_t y = egg.y;

    std::vector<Player> players = getPlayersByCoord(x, y);

    if (players.size() == 0)
        return;
    players[0].setFatherId(egg.getFatherId());
    removeEgg(eggId);
}

void zappy::game::GameState::removeEgg(const int &eggId)
{
    for (auto it = _eggs.begin(); it != _eggs.end(); it++) {
        if (it->getId() == eggId) {
            _eggs.erase(it);
            return;
        }
    }
    throw GameError("Egg " + std::to_string(eggId) + " not found", "Game");
}

void zappy::game::GameState::removePlayer(const int &id)
{
    for (auto it = _players.begin(); it != _players.end(); it++) {
        if (it->getId() == id) {
            _players.erase(it);
            return;
        }
    }
    throw GameError("Player " + std::to_string(id) + " not found", "Game");
}

std::vector<zappy::game::Player> zappy::game::GameState::getPlayersByCoord(const size_t &x, const size_t &y)
{
    std::vector<Player> players;

    for (Player &player : _players) {
        if (player.getId() != -1 && player.x == x && player.y == y)
            players.push_back(player);
    }
    return players;
}

zappy::game::Egg &zappy::game::GameState::getEggById(const int &eggId)
{
    for (Egg &egg : this->_eggs) {
        if (egg.getId() == eggId)
            return egg;
    }
    throw GameError("Egg " + std::to_string(eggId) + " not found", "Game");
}

zappy::game::Player &zappy::game::GameState::getPlayerById(const int &id)
{
    for (Player &player : _players) {
        if (player.getId() == id)
            return player;
    }
    throw GameError("Player " + std::to_string(id) + " not found", "Game");
}

void zappy::game::GameState::endGame(const std::string &teamName)
{
    std::cout << teamName << " wins" << std::endl;
}
