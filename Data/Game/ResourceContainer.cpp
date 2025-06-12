/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ResourceContainer.hpp
*/

#include "ResourceContainer.hpp"

void zappy::game::ResourceContainer::clear()
{
    constexpr auto noResource = 0;
    this->_resources.fill(noResource);
}

void zappy::game::ResourceContainer::addResource(Resource resource, size_t quantity)
{
    this->_resources[castResource(resource)] += quantity;
}

void zappy::game::ResourceContainer::addSingleResource(Resource resource)
{
    this->_resources[castResource(resource)] += 1;
}

void zappy::game::ResourceContainer::removeResource(Resource resource, size_t quantity)
{
    if (this->_resources[castResource(resource)] <= quantity)
        this->_resources[castResource(resource)] = 0;
    else
        this->_resources[castResource(resource)] -= quantity;
}

size_t zappy::game::ResourceContainer::getResourceQuantity(Resource resource) const
{
    return this->_resources[castResource(resource)];
}
