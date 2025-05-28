//
// EPITECH PROJECT, 2025
// Player Inventory
// File description:
// Player Inventory
//

#pragma once

#include <cstdint>
#include <map>

#define NO_ITEM 0

namespace zappy {
    namespace game {
        namespace player {
            enum class Item : uint8_t {
                food,
                linemate,
                deraumere,
                sibur,
                mendiane,
                phiras,
                thrystame
            };

            class Inventory {
            public:
                Inventory();
                ~Inventory() = default;

                void addItem(const Item &item);
                [[nodiscard]] bool removeItem(const Item &item);
                void clearInventory();

            private:
                std::map<Item, size_t> _items;
            };
        }  // namespace ZappyPlayer
    }
}
