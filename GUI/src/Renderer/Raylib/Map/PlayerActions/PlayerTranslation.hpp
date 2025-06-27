/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerTranslation.hpp
*/

#pragma once


#include "APlayerAction.hpp"
#include "IFloor.hpp"

#include <memory>

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerTranslation : public APlayerAction
            {
                public:
                    PlayerTranslation(
                        const int &playerId,
                        const ActionType &actionType,
                        const Translation &movement,
                        std::shared_ptr<IFloor> floor,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    ~PlayerTranslation() override = default;

                    void update(const float &deltaUnits, APlayerModel &player);

                    void finishAction(APlayerModel &player);

                private:
                    Translation _movement;
                    std::shared_ptr<IFloor> _floor;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
