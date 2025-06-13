//
// EPITECH PROJECT, 2025
// Inventory
// File description:
// Inventory
//

#include "ServerInventory.hpp"
#include <cstddef>
#include <sstream>

zappy::game::player::InventoryServer::InventoryServer()
{
    constexpr int startFood = 10;
    this->_items[zappy::game::Resource::FOOD] = startFood;
}


void zappy::game::player::InventoryServer::clearInventory()
{
    this->_items.clear();
}

