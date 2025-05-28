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
    Direction orientation,
    size_t level
) : id(id), level(level), x(x), y(y), orientation(orientation)
{}

void zappy::game::Player::stepForward()
{
    switch (orientation) {
        case NORTH:
            y--;
            break;
        case EAST:
            x++;
            break;
        case SOUTH:
            y++;
            break;
        case WEST:
            x--;
            break;
    }
}

void zappy::game::Player::ejectFrom(Direction direction)
{
    stopPraying();
    switch (direction) {
        case NORTH:
            y++;
            break;
        case EAST:
            x--;
            break;
        case SOUTH:
            y--;
            break;
        case WEST:
            x++;
            break;
    }
}

void zappy::game::Player::collectRessource(Ressource resource, size_t quantity)
{
    _inventory.addResource(resource, quantity);
}

void zappy::game::Player::dropRessource(Ressource resource, size_t quantity)
{
    _inventory.removeResource(resource, quantity);
}
