/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AFloor.hpp
*/

#pragma once

#include "IFloor.hpp"
#include "Map.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class AFloor : public IFloor {
                public:
                    AFloor(const zappy::game::Map &map)
                        : _map(map), _spacing(1), _width(0), _height(0) {};
                    virtual ~AFloor() = default;

                    // Setters
                    void setSpacing(int spacing) override;
                    void setWidth(int width) override;
                    void setHeight(int height) override;

                    // Getters
                    int getSpacing() const override;
                    int getWidth() const override;
                    int getHeight() const override;

                    // Draw
                    void draw() const override;

                private:
                    const zappy::game::Map &_map;
                    int _spacing;
                    int _width;
                    int _height;
            };
        }
    } // namespace gui
} // namespace zappy
