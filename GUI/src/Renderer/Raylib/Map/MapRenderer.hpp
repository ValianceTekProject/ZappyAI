/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once
#include "IFloor.hpp"
#include "Map.hpp"
#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class MapRenderer {
                public:
                    MapRenderer();
                    ~MapRenderer() = default;

                    void init();

                private:
                    const std::shared_ptr<game::Map> _map;
                    IFloor _floor;
            };
        }
    }
}
