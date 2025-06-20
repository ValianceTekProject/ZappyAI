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
                    FlatFloor(const size_t &width, const size_t &height, const float &tileSize = 10);
                    ~FlatFloor() = default;

                    void init() override;
                    void update() const override;
                    void render() const override;

                    Vector3 getGapFromOrientation(const game::Orientation &orientation) override;
                    Vector3 getNorthVector(const game::Orientation &orientation) override;

                    Vector3 get3DCoords(const int &x, const int &y) const override;

                private:
                    Texture2D _texture;
                    Model _model;
            };
        }
    } // namespace gui
} // namespace zappy
