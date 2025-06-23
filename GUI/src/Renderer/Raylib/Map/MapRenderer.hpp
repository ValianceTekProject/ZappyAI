/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once

#include "Map.hpp"
#include "FlatFloor.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class MapRenderer {
                public:
                    MapRenderer(const std::shared_ptr<game::Map> map);
                    ~MapRenderer() = default;

                    void init();

                    void update();

                    void render();

                private:
                    const std::shared_ptr<game::Map> _map;

                    std::unique_ptr<IFloor> _floor;
            };
        }
    }
}
