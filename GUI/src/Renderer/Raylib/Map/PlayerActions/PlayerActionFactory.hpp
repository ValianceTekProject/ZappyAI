/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.hpp
*/

#pragma once

#include "PlayerTranslation.hpp"
#include "PlayerRotation.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerActionFactory
            {
                public:
                    PlayerActionFactory() = delete;
                    ~PlayerActionFactory() = delete;

                    static std::unique_ptr<IPlayerAction> createTranslation(
                        const int &playerId,
                        const ActionType &actionType,
                        const Translation &translation,
                        std::shared_ptr<IFloor> floor,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );

                    static std::unique_ptr<IPlayerAction> createRotation(
                        const int &playerId,
                        const ActionType &actionType,
                        const Rotation &rotation,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
