/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IPlayerModel.hpp
*/

#pragma once

#include <GL/glew.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IPlayerModel {
                public:
                    virtual ~IPlayerModel() = default;

                    virtual void init() = 0;

                    virtual void update() = 0;

                    virtual void walk() = 0;
                    virtual void ejected() = 0;
                    virtual void idle() = 0;

                    virtual void render() = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
