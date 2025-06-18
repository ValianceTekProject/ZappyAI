/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Resource.cpp
*/

#include "Resource.hpp"

size_t zappy::game::castResource(const Resource &res)
{
    return static_cast<size_t>(res);
}

const std::string &zappy::game::getName(const Resource &res)
{
    return names[castResource(res)];
}

zappy::game::Resource zappy::game::getResource(const std::string &name)
{
    for (size_t i = 0; i < RESOURCE_QUANTITY; i++) {
        if (names[i] == name)
            return static_cast<Resource>(i);
    }
    throw GameError("Resource not found", "Resource");
}
