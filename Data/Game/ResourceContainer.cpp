/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** RessourceContainer.hpp
*/

#include "ResourceContainer.hpp"

void zappy::game::RessourceContainer::clear()
{
    _resources.fill(0);
}

void zappy::game::RessourceContainer::addResource(Resource resource, size_t quantity)
{
    _resources[castResource(resource)] += quantity;
}

void zappy::game::RessourceContainer::removeResource(Resource resource, size_t quantity)
{
    if (_resources[castResource(resource)] <= quantity)
        _resources[castResource(resource)] = 0;
    else
        _resources[castResource(resource)] -= quantity;
}

size_t zappy::game::RessourceContainer::getResourceQuantity(Resource resource) const
{
    return _resources[castResource(resource)];
}
