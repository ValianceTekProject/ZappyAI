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

            private:
                bool _shouldClose;
        };
    }
}
