/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once

#include "AResourceModel.hpp"
#include "Orientation.hpp"
#include "RendererError.hpp"
#include "BasicResourceModel.hpp"

#include "Map.hpp"
#include "FlatFloor.hpp"

#include "PlayerActionFactory.hpp"

// #include "AResourceModel.hpp"
#include "AEggModel.hpp"
#include "APlayerModel.hpp"
#include "Resource.hpp"

#include "BroadcastEffectFactory.hpp"

#include <memory>
#include <vector>
#include <unordered_map>
#include <queue>
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

                    void _addRotation(const APlayerModel &player, const float &angle);

                    void _updateMovements(const float &deltaUnits);

                    void _updateBroadcasts(const float &deltaUnits);

                    const std::shared_ptr<game::Map> _map;

                    std::chrono::steady_clock::time_point _lastTime;

                    std::shared_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<AEggModel>> _eggs;
                    std::vector<std::unique_ptr<APlayerModel>> _players;
                    std::array<std::unique_ptr<BasicResourceModel>, zappy::game::RESOURCE_QUANTITY> _resourceModels;

                    std::unordered_map<int, std::queue<std::unique_ptr<IPlayerAction>>> _playerActionQueues;

                    // std::vector<std::unique_ptr<IBroadcastEffect>> _broadcasts;
            };
        }
    }
}
