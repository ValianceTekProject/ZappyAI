/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** RessourceContainer.hpp
*/

#include "RessourceContainer.hpp"

void zappy::game::RessourceContainer::clear()
{
    _resources.clear();
}

void zappy::game::RessourceContainer::addResource(Ressource resource, size_t quantity)
{
    if (_resources.find(resource) == _resources.end())
        _resources[resource] = quantity;
    else
        _resources[resource] += quantity;
}

void zappy::game::RessourceContainer::removeResource(Ressource resource, size_t quantity)
{
    if (_resources.find(resource) == _resources.end())
        return;
    if (_resources[resource] < quantity)
        _resources.erase(resource);
    else
        _resources[resource] -= quantity;
}

const size_t &zappy::game::RessourceContainer::getResourceQuantity(Ressource resource) const
{
    if (_resources.find(resource) == _resources.end())
        return 0;
    return _resources.at(resource);
}
