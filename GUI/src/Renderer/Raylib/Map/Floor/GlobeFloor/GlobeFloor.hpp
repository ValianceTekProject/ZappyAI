/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** GlobeFloor.hpp
*/

#pragma once
#include "../AFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class GlobeFloor : public AFloor {
                public:
                    GlobeFloor(size_t width, size_t height, size_t tileSize);
                    ~GlobeFloor() = default;

                    void render() const override;

                private:
                    int _radius;
            };
        }
    } // namespace gui
} // namespace zappy
