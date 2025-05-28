/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.hpp
*/

#include "Inventory.hpp"

namespace zappy {
    namespace game {
        class Player
        {
            public:
                enum Direction {
                    NORTH,
                    EAST,
                    SOUTH,
                    WEST
                };

                size_t id;
                size_t level;
                size_t x;
                size_t y;
                Direction orientation;

                Player(
                    size_t id,
                    size_t x,
                    size_t y,
                    Direction orientation,
                    size_t level = 1
                );
                ~Player() = default;

                void pray() { _isPraying = true; }
                bool isPraying() const { return _isPraying; }
                void stopPraying() { _isPraying = false; }

                void lookLeft() { this->orientation = static_cast<Direction>((this->orientation - 1 + 4) % 4); }
                void lookRight() { this->orientation = static_cast<Direction>((this->orientation + 1) % 4); }

                void stepForward();

                void ejectFrom(Direction direction);

                const Inventory &getInventory() const { return _inventory; }

                void collectRessource(Ressource resource, size_t quantity = 1);
                void dropRessource(Ressource resource, size_t quantity = 1);

            private:
                bool _isPraying;

                Inventory _inventory;
        };
    }
}
