/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once

#include "RendererError.hpp"

#include "Map.hpp"
#include "FlatFloor.hpp"

// #include "AResourceModel.hpp"
#include "AEggModel.hpp"
#include "APlayerModel.hpp"

#include <memory>
#include <vector>
#include <chrono>

namespace zappy {
    namespace gui {
        namespace raylib {
            class MapRenderer {
                public:
                    constexpr static int FORWARD_TIME = 7;
                    constexpr static int ROTATION_TIME = 7;
                    constexpr static int EXPULSION_TIME = 1;
                    constexpr static int NO_ANIMATION = 0;

                    struct Translation {
                        int id;
                        Vector3 destination;
                        Vector3 translationVector;
                        int timeUnit;     //! (comment is to remove) action time duration
                    };

                    struct Rotation {
                        int id;
                        Vector3 destination;
                        Vector3 deltaPerStep;
                        int timeUnits;
                        float elapsedTime;
                    };

                    MapRenderer(const std::shared_ptr<game::Map> map);
                    ~MapRenderer() = default;

                    void init();

                    void update(const int &frequency);

                    void render();

                    void addEgg(std::unique_ptr<AEggModel> egg);
                    void addPlayer(std::unique_ptr<APlayerModel> player);

                    void setEggPosition(const int &id, const int &x, const int &y);
                    void setPlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation);

                    void playerLook(const int &id, const game::Orientation &orientation);
                    void playerLookLeft(const int &id);
                    void playerLookRight(const int &id);

                    void playerForward(const int &id, const int &x, const int &y);
                    void playerExpulsion(const int &id, const int &x, const int &y);

                    void removePlayer(const int &id);
                    void removeEgg(const int &id);

                private:
                    APlayerModel &_getPlayer(const int &id);
                    const APlayerModel &_getPlayer(const int &id) const;
                    AEggModel &_getEgg(const int &id);
                    const AEggModel &_getEgg(const int &id) const;

                    void _updateTranslations(const int &frequency);
                    void _updateRotations(const float &deltaUnits);

                    const std::shared_ptr<game::Map> _map;

                    std::chrono::steady_clock::time_point _lastTime;

                    std::unique_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<AEggModel>> _eggs;
                    std::vector<std::unique_ptr<APlayerModel>> _players;

                    std::vector<Translation> _translations;
                    std::vector<Rotation> _rotations;
            };
        }
    }
}
