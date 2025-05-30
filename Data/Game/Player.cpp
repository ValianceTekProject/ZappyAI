/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.cpp
*/

#include "Player.hpp"

void operator++(zappy::game::Orientation &orientation, int)
{
    orientation = static_cast<zappy::game::Orientation>((static_cast<int>(orientation) + 1) % 4);
}

void operator--(zappy::game::Orientation &orientation, int)
{
    orientation = static_cast<zappy::game::Orientation>((static_cast<int>(orientation) - 1 + 4) % 4);
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
    size_t id,
    size_t x,
    size_t y,
    Orientation orientation,
    size_t level
) :
    id(id),
    level(level),
    x(x),
    y(y),
    orientation(orientation),
    hasHatch(false),
    _isPraying(false)
{}

void zappy::game::Player::stepForward()
{
    switch (orientation) {
        case Orientation::NORTH:
            y--;
            break;
        case Orientation::EAST:
            x++;
            break;
        case Orientation::SOUTH:
            y++;
            break;
        case Orientation::WEST:
            x--;
            break;
    }
}

void zappy::game::Player::ejectFrom(Orientation direction)
{
    stopPraying();
    switch (direction) {
        case Orientation::NORTH:
            y++;
            break;
        case Orientation::EAST:
            x--;
            break;
        case Orientation::SOUTH:
            y--;
            break;
        case Orientation::WEST:
            x++;
            break;
    }
}

void zappy::game::Player::collectRessource(Resource resource, size_t quantity)
{
    _inventory.addResource(resource, quantity);
}

void zappy::game::Player::dropRessource(Resource resource, size_t quantity)
{
    _inventory.removeResource(resource, quantity);
}
