/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Ressource.cpp
*/

#include "Ressource.hpp"

// Ressources
const std::string zappy::game::names[COUNT - 1] = {
    "food",
    "linemate",
    "deraumere",
    "sibur",
    "mendiane",
    "phiras",
    "thystame"
};

const std::string &zappy::game::getName(Ressource res)
{
    return names[res];
}

zappy::game::Ressource zappy::game::getRessource(const std::string &name)
{
    for (int i = 0; i < COUNT; i++) {
        if (names[i] == name)
            return static_cast<Ressource>(i);
    }
    return NONE;
}
