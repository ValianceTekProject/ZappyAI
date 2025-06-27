/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.cpp
*/

#include "Player.hpp"

zappy::game::Player::Player(
    int id,
    int x,
    int y,
    Orientation orientation,
    size_t level
) :
    Egg::Egg(id, x, y),
    level(level),
    orientation(orientation),
    _isPraying(false)
{}

void zappy::game::Player::stepForward(int width, int height)
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

    if (x > width || x < 0)
        x = (x + width) % width;
    if (y > height || y < 0)
        y = (y + height) % height;
}

void zappy::game::Player::ejectFrom(Orientation playerOrientation, int width, int height)
{
    stopPraying();
    switch (playerOrientation) {
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

    if (x > width || x < 0)
        x = (x + width) % width;
    if (y > height || y < 0)
        y = (y + height) % height;
}

void zappy::game::Player::collectRessource(Resource resource, std::size_t quantity)
{
    this->_inventory.addResource(resource, quantity);
}

void zappy::game::Player::dropRessource(Resource resource, std::size_t quantity)
{
    this->_inventory.removeResource(resource, quantity);
}
