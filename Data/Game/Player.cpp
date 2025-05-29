/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.cpp
*/

#include "Player.hpp"


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

void zappy::game::Player::lookLeft()
{
    orientation = static_cast<Orientation>((static_cast<int>(orientation) - 1 + 4) % 4);
}

void zappy::game::Player::lookRight()
{
    orientation = static_cast<Orientation>((static_cast<int>(orientation) + 1) % 4);
}

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
