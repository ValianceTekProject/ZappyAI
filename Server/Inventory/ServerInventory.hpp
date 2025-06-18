//
// EPITECH PROJECT, 2025
// Player Inventory
// File description:
// Player Inventory
//

#pragma once

#include <cstdint>
#include <map>

#include "Inventory.hpp"

namespace zappy {
    namespace game {
        namespace player {

            class InventoryServer :  public Inventory {
            public:
                InventoryServer();
                ~InventoryServer() = default;

                void clearInventory();

            private:
                std::map<zappy::game::Resource, size_t> _items;
            };
        }  // namespace ZappyPlayer
    }
}
