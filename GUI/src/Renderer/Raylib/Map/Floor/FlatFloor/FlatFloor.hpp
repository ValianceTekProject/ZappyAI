/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.hpp
*/

#pragma once
#include "AFloor.hpp"

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

                    virtual Translation createTranslation(const APlayerModel &player, const int &x, const int &y, const int &timeUnit) override;

                    void translate(const float &deltaUnits, const Vector3 &translationVector, Vector3 &destination, APlayerModel &player) override;

                private:
                    Texture2D _texture;
                    Model _model;
                    void _checkOverlap(APlayerModel &player, Vector3 &destination);
            };
        }
    } // namespace gui
} // namespace zappy
