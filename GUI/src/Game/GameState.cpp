/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameState.cpp
*/

#include "GameState.hpp"

void zappy::game::GameState::updatePlayerPosition(
    const int &id,
    const int &x,
    const int &y,
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

void zappy::game::GameState::PlayerExpulsion(const int &id)
{
    Player &playerThatExpelled = getPlayerById(id);

    auto players = getPlayersByCoord(playerThatExpelled.x, playerThatExpelled.y);

    for (Player &player : players) {
        if (player.getId() == id)
            continue;
        player.ejectFrom(playerThatExpelled.orientation);
    }
}

void zappy::game::GameState::PlayerBroadcast(const int &, const std::string &)
{}

void zappy::game::GameState::StartIncantation(
    const int &, const int &,
    const int &,
    const std::vector<int> &playerIds
) {
    for (int id : playerIds) {
        Player &player = getPlayerById(id);
        player.pray();
    }
}

void zappy::game::GameState::EndIncantation(const int &x, const int &y, const bool &result)
{
    auto players = getPlayersByCoord(x, y);

    for (Player &player : players) {
        if (!player.isPraying())
            continue;
        player.stopPraying();
        if (result)
            player.level += 1;
    }
}

void zappy::game::GameState::hatchEgg(const int &eggId)
{
    Egg &egg = getEggById(eggId);
    int x = egg.x;
    int y = egg.y;

    auto players = getPlayersByCoord(x, y);

    if (players.empty())
        return;

    Player &player = players[0].get();
    player.setFatherId(egg.getFatherId());

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

zappy::game::Egg &zappy::game::GameState::getEggById(const int &eggId)
{
    for (Egg &egg : this->_eggs) {
        if (egg.getId() == eggId)
            return egg;
    }
    throw GameError("Egg " + std::to_string(eggId) + " not found", "Game");
}

const zappy::game::Egg &zappy::game::GameState::getEggById(const int &eggId) const
{
    for (const Egg &egg : this->_eggs) {
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

const zappy::game::Player &zappy::game::GameState::getPlayerById(const int &id) const
{
    for (const Player &player : _players) {
        if (player.getId() == id)
            return player;
    }
    throw GameError("Player " + std::to_string(id) + " not found", "Game");
}

std::vector<std::reference_wrapper<zappy::game::Egg>> zappy::game::GameState::getEggsByCoord(const int &x, const int &y)
{
    std::vector<std::reference_wrapper<Egg>> eggs;

    for (Egg &egg : _eggs) {
        if (egg.x == x && egg.y == y)
            eggs.push_back(std::ref(egg));
    }
    return eggs;
}

std::vector<std::reference_wrapper<const zappy::game::Egg>> zappy::game::GameState::getEggsByCoord(const int &x, const int &y) const
{
    std::vector<std::reference_wrapper<const Egg>> eggs;

    for (const Egg &egg : _eggs) {
        if (egg.x == x && egg.y == y)
            eggs.push_back(std::cref(egg));
    }
    return eggs;
}

std::vector<std::reference_wrapper<zappy::game::Player>> zappy::game::GameState::getPlayersByCoord(const int &x, const int &y)
{
    std::vector<std::reference_wrapper<Player>> players;

    for (Player &player : _players) {
        if (player.getId() != -1 && player.x == x && player.y == y)
            players.push_back(std::ref(player));
    }
    return players;
}

std::vector<std::reference_wrapper<const zappy::game::Player>> zappy::game::GameState::getPlayersByCoord(const int &x, const int &y) const
{
    std::vector<std::reference_wrapper<const Player>> players;

    for (const Player &player : _players) {
        if (player.getId() != -1 && player.x == x && player.y == y)
            players.push_back(std::cref(player));
    }
    return players;
}

void zappy::game::GameState::endGame(const std::string &teamName)
{
    std::cout << teamName << " wins" << std::endl;
}
