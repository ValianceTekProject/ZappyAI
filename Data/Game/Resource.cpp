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

const std::string &zappy::game::getName(Resource res)
{
    return names[castResource(res)];
}

zappy::game::Resource zappy::game::getResource(const std::string &name)
{
    for (int i = 0; i < RESOURCE_QUANTITY; i++) {
        if (names[i] == name)
            return static_cast<Resource>(i);
    }
    return Resource::RESOURCE_SIZE;
}
