//
// EPITECH PROJECT, 2025
// Inventory
// File description:
// Inventory
//

#include "Inventory.hpp"
#include <cstddef>
#include <sstream>

zappy::game::player::Inventory::Inventory()
{
    this->_items[Item::food] = 10;
}

void zappy::game::player::Inventory::addItem(const Item &item)
{
    if (this->_items.find(item) != this->_items.end()) {
        this->_items[item] += 1;
        return;
    }
    this->_items[item] = 1;
}

bool zappy::game::player::Inventory::removeItem(const Item &item)
{
    if (this->_items.find(item) != this->_items.end()) {
        if (this->_items[item] == NO_ITEM)
            return false;
        this->_items[item] -= 1;
        return true;
    }
    return false;
}

void zappy::game::player::Inventory::clearInventory()
{
    this->_items.clear();
}

