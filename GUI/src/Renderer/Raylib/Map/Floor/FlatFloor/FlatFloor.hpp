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
                    FlatFloor(size_t width, size_t height, size_t tileSize = 10);
                    ~FlatFloor() = default;

                    void init() override;
                    void update() const override;
                    void render() const override;

                private:
                    Texture2D _texture;
                    Model _model;
            };
        }
    } // namespace gui
} // namespace zappy
