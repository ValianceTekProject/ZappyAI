/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ResourceContainer.hpp
*/

#include "ResourceContainer.hpp"

void zappy::game::ResourceContainer::clear()
{
    _resources.fill(0);
}

void zappy::game::ResourceContainer::addResource(Resource resource, size_t quantity)
{
    _resources[castResource(resource)] += quantity;
}

void zappy::game::ResourceContainer::removeResource(Resource resource, size_t quantity)
{
    if (_resources[castResource(resource)] <= quantity)
        _resources[castResource(resource)] = 0;
    else
        _resources[castResource(resource)] -= quantity;
}

size_t zappy::game::ResourceContainer::getResourceQuantity(Resource resource) const
{
    return _resources[castResource(resource)];
}
