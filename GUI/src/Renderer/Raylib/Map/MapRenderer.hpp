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
                    struct Translation {
                        const int id;
                        Vector2 start;
                        Vector2 current;
                        Vector2 destination;
                        Vector2 translationVector;
                    };

                    struct Rotation {
                        const int id;
                        float start;
                        float current;
                        float destination;
                    };

                    MapRenderer(const std::shared_ptr<game::Map> map);
                    ~MapRenderer() = default;

                    void init();

                    void update(const int &frequency);

                    void render();

                    void addEgg(std::unique_ptr<IEggModel> egg);
                    void addPlayer(std::unique_ptr<IPlayerModel> player);

                    void setEggPosition(const int &id, const size_t &x, const size_t &y);
                    void setPlayerPosition(const int &id, const size_t &x, const size_t &y, const game::Orientation &orientation);

                    void playerLook(const int &id, const game::Orientation &orientation);
                    void playerLookLeft(const int &id);
                    void playerLookRight(const int &id);

                    void playerForward(const int &id, const int &x, const int &y);
                    void playerExpulsion(const int &id, const int &x, const int &y);

                    void removePlayer(const int &id);
                    void removeEgg(const int &id);

                private:
                    void _translate(const Translation &translation, const int &frequency);
                    void _rotate(const Rotation &rotation, const int &frequency);

                    const std::shared_ptr<game::Map> _map;

                    std::unique_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<IPlayerModel>> _players;
                    std::vector<std::unique_ptr<IEggModel>> _eggs;

                    std::vector<Translation> _translations;
                    std::vector<Rotation> _rotations;
            };
        }
    }
}
