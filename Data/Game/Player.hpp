/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.hpp
*/

#pragma once

#include "Egg.hpp"
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
        Orientation operator-(const Orientation &orientation);
        Orientation convertOrientation(const std::string &orientation);

        class Player : public Egg
        {
            public:
                size_t level;
                Orientation orientation;
                std::string teamName;

                explicit Player(
                    int id,
                    size_t x,
                    size_t y,
                    Orientation orientation = Orientation::NORTH,
                    size_t level = 1
                );
                ~Player() = default;

                void pray() { this->_isPraying = true; }
                bool isPraying() const { return this->_isPraying; }
                void stopPraying() { this->_isPraying = false; }

                void lookLeft() { this->orientation--; }
                void lookRight() { this->orientation++; }

                void stepForward();

                void ejectFrom(Orientation playerOrientation);

                void setInventory(const Inventory &inventory) { this->_inventory = inventory; }
                const Inventory &getInventory() const { return this->_inventory; }

                void collectRessource(Resource resource, size_t quantity = 1);
                void dropRessource(Resource resource, size_t quantity = 1);

            private:
                bool _isPraying;

                Inventory _inventory;
        };
    }
}
