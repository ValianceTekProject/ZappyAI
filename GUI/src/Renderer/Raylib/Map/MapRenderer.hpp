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
                    void addPlayer(std::unique_ptr<IPlayerModel> player);

                    void setEggPosition(const int &id, const size_t &x, const size_t &y);
                    void setPlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation);

                    void removePlayer(const int &id);
                    void removeEgg(const int &id);

                private:
                    std::unique_ptr<IEggModel> getEgg(const int &id);
                    std::unique_ptr<IPlayerModel> getPlayer(const int &id);

                    const std::shared_ptr<game::Map> _map;

                    std::unique_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<IPlayerModel>> _players;

                    std::vector<std::unique_ptr<IEggModel>> _eggs;
            };
        }
    }
}
