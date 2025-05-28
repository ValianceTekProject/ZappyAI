/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NCursesRenderer.cpp
*/

#pragma once

#include "IRenderer.hpp"

#include <ncurses.h>

namespace gui {
    class NCursesRenderer : public IRenderer
    {
        public:
            NCursesRenderer();
            ~NCursesRenderer();


    };
}
