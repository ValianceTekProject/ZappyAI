/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.cpp
*/

#include "Player.hpp"

void zappy::game::operator++(zappy::game::Orientation &orientation, int)
{
    orientation = static_cast<zappy::game::Orientation>((static_cast<int>(orientation) + 1) % 4);
}

void zappy::game::operator--(zappy::game::Orientation &orientation, int)
{
    orientation = static_cast<zappy::game::Orientation>((static_cast<int>(orientation) - 1 + 4) % 4);
}

zappy::game::Orientation operator-(const zappy::game::Orientation &orientation)
{
    return static_cast<zappy::game::Orientation>((static_cast<int>(orientation) + 2) % 4);
}

zappy::game::Orientation zappy::game::convertOrientation(const std::string &orientation)
{
    if (orientation == "NORTH" || orientation == "N")
        return zappy::game::Orientation::NORTH;
    if (orientation == "EAST" || orientation == "E")
        return zappy::game::Orientation::EAST;
    if (orientation == "SOUTH" || orientation == "S")
        return zappy::game::Orientation::SOUTH;
    if (orientation == "WEST" || orientation == "W")
        return zappy::game::Orientation::WEST;
    return zappy::game::Orientation::NORTH;
}

zappy::game::Player::Player(
    int id,
    size_t x,
    size_t y,
    Orientation orientation,
    size_t level
) :
    Egg::Egg(id, x, y),
    level(level),
    orientation(orientation),
    _isPraying(false)
{}

void zappy::game::Player::stepForward()
{
    switch (orientation) {
        case Orientation::NORTH:
            this->y--;
            break;
        case Orientation::EAST:
            this->x++;
            break;
        case Orientation::SOUTH:
            this->y++;
            break;
        case Orientation::WEST:
            this->x--;
            break;
    }
}

void zappy::game::Player::ejectFrom(Orientation playerOrientation)
{
    stopPraying();
    Orientation ejectFromOrientation = -playerOrientation;
    switch (ejectFromOrientation) {
        case Orientation::NORTH:
            this->y++;
            break;
        case Orientation::EAST:
            this->x--;
            break;
        case Orientation::SOUTH:
            this->y--;
            break;
        case Orientation::WEST:
            this->x++;
            break;
    }
}

void zappy::game::Player::collectRessource(Resource resource, std::size_t quantity)
{
    this->_inventory.addResource(resource, quantity);
}

void zappy::game::Player::dropRessource(Resource resource, std::size_t quantity)
{
    this->_inventory.removeResource(resource, quantity);
}
