/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AFloor.hpp
*/

#pragma once

#include "IFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class AFloor : public IFloor {
                public:
                    AFloor();
                    ~AFloor() = default;

                    // Setters
                    void setGridSize(int size) override;
                    void setSpacing(int spacing) override;
                    void setWidth(int width);
                    void setHeight(int height);

                    // Getters
                    int getGridSize() const override;
                    int getSpacing() const override;
                    int getWidth() const override;
                    int getHeight() const override;

                private:
                    int _gridSize;
                    int _spacing;
                    int _width;
                    int _height;
            };
        }
    } // namespace gui
} // namespace zappy
