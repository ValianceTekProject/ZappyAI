/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NCursesRenderer.cpp
*/

#pragma once

#include "IRenderer.hpp"

#include <ncurses.h>

namespace zappy {
    namespace gui {
        class NCursesRenderer : public IRenderer
        {
            public:
                NCursesRenderer();
                ~NCursesRenderer();

                void init() override;

                void handleInput() override;
                void update() override;

                void render() override;

                void close() override;

            private:
                WINDOW *_window;
        };
    }
}
