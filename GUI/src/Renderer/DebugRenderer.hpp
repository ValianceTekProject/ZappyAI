/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** DebugRenderer.cpp
*/

#pragma once

#include "ARenderer.hpp"

#include <ncurses.h>
#include <sstream>

namespace zappy {
    namespace gui {
        class DebugRenderer : public ARenderer
        {
            public:
                DebugRenderer();
                ~DebugRenderer() = default;

                void init() override {}

                void handleInput() override {}
                void update() override {}

                void render() const override {}

                bool shouldClose() const override { return false; }

                void PlayerExpulsion(const int &id) override;

                void PlayerBroadcast(const int &id, const std::string &message) override;

                void StartIncantation(
                    const int &x, const int &y,
                    const int &level,
                    const std::vector<int> &playerIds
                ) override;
                void EndIncantation(const int &x, const int &y, const bool &result) override;

            private:
                bool _shouldClose;
        };
    }
}
