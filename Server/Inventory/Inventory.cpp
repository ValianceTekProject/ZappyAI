//
// EPITECH PROJECT, 2025
// Inventory
// File description:
// Inventory
//

#include "Inventory.hpp"
#include <cstddef>
#include <sstream>

zappy::game::player::InventoryServer::InventoryServer()
{
    this->_items[zappy::game::Ressource::FOOD] = START_FOOD;
}


void zappy::game::player::InventoryServer::clearInventory()
{
    this->_items.clear();
}

