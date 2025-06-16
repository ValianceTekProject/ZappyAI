/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.hpp
*/

#pragma once
#include "../AFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class FlatFloor : public AFloor {
                public:
                    FlatFloor(const zappy::game::Map &map);
                    ~FlatFloor() = default;

                    void draw() const override;
            };
        }
    } // namespace gui
} // namespace zappy
