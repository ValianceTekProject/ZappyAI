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

#include "Map.hpp"
#include "FlatFloor.hpp"

// #include "AResourceModel.hpp"
#include "AEggModel.hpp"
#include "APlayerModel.hpp"
#include "Resource.hpp"

#include <memory>
#include <optional>
#include <vector>
#include <chrono>
#include "Incantation.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class MapRenderer {
                public:
                    constexpr static int FORWARD_TIME = 7;
                    constexpr static int ROTATION_TIME = 7;
                    constexpr static int EXPULSION_TIME = 1;
                    constexpr static int NO_ANIMATION = 0;

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

                    void renderResources();
                    void renderIncantations();

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

                    void removePlayer(const int &id);
                    void removeEgg(const int &id);

                    void setIncantationTile(const int &x, const int &y);
                    void clearIncantationTile(const int &x, const int &y);

                    private:
                    APlayerModel &_getPlayer(const int &id);
                    const APlayerModel &_getPlayer(const int &id) const;

                    AEggModel &_getEgg(const int &id);
                    const AEggModel &_getEgg(const int &id) const;

                    void _addRotation(const APlayerModel &player, const float &angle);

                    void _updateTranslations(const float &deltaUnits);
                    void _updateRotations(const float &deltaUnits);
                    void _updateIncantationAnimation(float deltaTime);

                    const std::shared_ptr<game::Map> _map;

                    std::chrono::steady_clock::time_point _lastTime;

                    std::unique_ptr<IFloor> _floor;

                    std::vector<std::unique_ptr<AEggModel>> _eggs;
                    std::vector<std::unique_ptr<APlayerModel>> _players;
                    std::array<std::unique_ptr<AResourceModel>, zappy::game::RESOURCE_QUANTITY> _resourceModels;

                    std::vector<std::unique_ptr<Incantation>> _incantations;

                    std::vector<Translation> _translations;
                    std::vector<Rotation> _rotations;
            };
        }
    }
}
