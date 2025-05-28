/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Tile.hpp
*/

#include <iostream>
#include <vector>

namespace gui {
    class Tile
    {
        public:
            Tile() = default;
            Tile(const Tile &other) = default;
            ~Tile() = default;

            void clear();

            void addResource(int resource, int quantity = 1);

            void removeResource(int resource, int quantity = 1);

            int getResourceQuantity(int resource) const;
            std::vector<std::string> getResources() const;

        private:
            std::vector<std::string> _resources;
    };
}
