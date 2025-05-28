/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Ressource.cpp
*/

#include "Ressource.hpp"

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
