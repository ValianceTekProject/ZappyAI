/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Player.hpp
*/

#pragma once

#include "Egg.hpp"
#include "Orientation.hpp"
#include "Inventory.hpp"

namespace zappy {
    namespace game {
        class Player : public Egg
        {
            public:
                size_t level;
                Orientation orientation;
                std::string teamName;

                explicit Player(
                    int id,
                    int x,
                    int y,
                    Orientation orientation = Orientation::NORTH,
                    size_t level = 1
                );
                ~Player() = default;

                void pray() { this->_isPraying = true; }
                bool isPraying() const { return this->_isPraying; }
                void stopPraying() { this->_isPraying = false; }

                void lookLeft() { this->orientation--; }
                void lookRight() { this->orientation++; }

                void stepForward(int width, int height);

                void ejectFrom(Orientation playerOrientation, int width, int height);

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
