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

                    // Getters
                    int getGridSize() const override;
                    int getSpacing() const override;

                private:
                    int gridSize;
                    int spacing;
            };
        }
    } // namespace gui
} // namespace zappy
