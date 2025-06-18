/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once

#include "Map.hpp"
#include "FlatFloor.hpp"
#include "IPlayerModel.hpp"
#include "IEggModel.hpp"

#include <memory>
#include <vector>

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

                    void addEgg(std::unique_ptr<IEggModel> egg);
                    void removeEgg(const int &id);

                    void addPlayer(std::unique_ptr<IPlayerModel> player);
                    void removePlayer(const int &id);

                private:
                    const std::shared_ptr<game::Map> _map;

                    std::unique_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<IPlayerModel>> _players;

                    std::vector<std::unique_ptr<IEggModel>> _eggs;
            };
        }
    }
}
