/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** Map.hpp
*/

#pragma once

#include "AResourceModel.hpp"
#include "RendererError.hpp"

#include "Map.hpp"
#include "FlatFloor.hpp"
#include "BasicResourceModel.hpp"

#include "PlayerActionFactory.hpp"

#include "AEggModel.hpp"
#include "APlayerModel.hpp"
#include "Resource.hpp"

#include "EffectFactory.hpp"

#include <memory>
#include <optional>
#include <vector>
#include <unordered_map>
#include <queue>
#include <chrono>

namespace zappy {
    namespace gui {
        namespace raylib {
            class MapRenderer {
                public:
                    MapRenderer(const std::shared_ptr<game::Map> map);
                    ~MapRenderer() = default;

                    void init();

                    void update(const int &frequency);

                    void render();

                    void setBroadcastType(const EffectType &type);
                    void setBroadcastColor(const Color &color);

                    void setIncantationType(const EffectType &type);
                    void setIncantationColor(const Color &color);

                    void addEgg(std::unique_ptr<AEggModel> egg);
                    void addPlayer(std::unique_ptr<APlayerModel> player);
                    void addResourceModel(const zappy::game::Resource &type, std::unique_ptr<AResourceModel> model);

                    void setEggPosition(const int &id, const int &x, const int &y);
                    void setPlayerPosition(const int &id, const int &x, const int &y, const game::Orientation &orientation);

                    void playerLook(const int &id, const game::Orientation &orientation);
                    void playerLookLeft(const int &id);
                    void playerLookRight(const int &id);

                    void playerForward(const int &id, const int &x, const int &y);
                    void playerExpulsion(const int &id, const int &x, const int &y);

                    void playerBroadcast(const int &id);

                    void startIncantation(const int &x, const int &y, const std::vector<int> &playerIds);
                    void endIncantation(const int &x, const int &y, const bool &result);

                    void removePlayer(const int &id);
                    void removeEgg(const int &id);

                    private:
                    APlayerModel &_getPlayer(const int &id);
                    const APlayerModel &_getPlayer(const int &id) const;

                    AEggModel &_getEgg(const int &id);
                    const AEggModel &_getEgg(const int &id) const;

                    void _addRotation(const APlayerModel &player, const float &angle);

                    void _updatePlayersAndEggs(const float &deltaUnits);
                    void _updateActions(const float &deltaUnits);
                    void _updatePlayerAfterAction(APlayerModel &player, const std::queue<std::shared_ptr<IPlayerAction>> &actions);
                    void _updateAnimActions(const float &deltaUnits);

                    void _renderPlayersAndEggs();
                    void _renderResources();

                    void _renderAnimActions();

                    const std::shared_ptr<game::Map> _map;
                    std::shared_ptr<IFloor> _floor;

                    EffectType _broadcastType;
                    Color _broadcastColor;

                    EffectType _incantationType;
                    Color _incantationColor;

                    std::vector<std::unique_ptr<AEggModel>> _eggs;
                    std::vector<std::unique_ptr<APlayerModel>> _players;
                    std::array<std::unique_ptr<AResourceModel>, zappy::game::RESOURCE_QUANTITY> _resourceModels;

                    std::chrono::steady_clock::time_point _lastTime;

                    std::unordered_map<int, std::queue<std::shared_ptr<IPlayerAction>>> _playerActionQueues;

                    std::vector<std::shared_ptr<APlayerAnimAction>> _playerAnimAction;

                    std::unordered_map<ssize_t, Vector2> _incantationMap;
            };
        }
    }
}
