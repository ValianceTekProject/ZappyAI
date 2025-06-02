/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.hpp
*/

#include "Inventory.hpp"
#include <string>

namespace zappy {
    namespace game {
        enum class Orientation {
            NORTH,
            EAST,
            SOUTH,
            WEST
        };
        void operator++(Orientation &orientation, int);
        void operator--(Orientation &orientation, int);
        Orientation convertOrientation(const std::string &orientation);

        class Player
        {
            public:
                size_t id;
                size_t level;
                size_t x;
                size_t y;
                Orientation orientation;
                std::string teamName;
                bool hasHatch;

                Player(
                    size_t id,
                    size_t x,
                    size_t y,
                    Orientation orientation,
                    size_t level = 1
                );
                ~Player() = default;

                void pray() { _isPraying = true; }
                bool isPraying() const { return _isPraying; }
                void stopPraying() { _isPraying = false; }

                void lookLeft() { orientation--; }
                void lookRight() { orientation++; }

                void stepForward();

                void ejectFrom(Orientation direction);

                void setInventory(const Inventory &inventory) { _inventory = inventory; }
                const Inventory &getInventory() const { return _inventory; }

                void collectRessource(Resource resource, size_t quantity = 1);
                void dropRessource(Resource resource, size_t quantity = 1);

            private:
                bool _isPraying;

                Inventory _inventory;
        };
    }
}
