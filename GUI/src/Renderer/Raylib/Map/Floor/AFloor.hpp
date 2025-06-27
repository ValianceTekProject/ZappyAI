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
                    AFloor(const size_t &width, const size_t &height, const float &tileSize);
                    ~AFloor() = default;

                    virtual void init() override;
                    virtual void update() const override;
                    virtual void render() const override;

                    // Setters
                    void setWidth(const size_t &width) override { this->_width = width; }
                    void setHeight(const size_t &height) override { this->_height = height; }
                    void setTileSize(const float &tileSize) override { this->_tileSize = tileSize; }

                    // Getters
                    size_t getWidth() const override { return _width; }
                    size_t getHeight() const override { return _height; }
                    float getTileSize() const override { return _tileSize; }

                    Vector3 getGapFromOrientation(const game::Orientation &orientation) override = 0;
                    Vector3 getNorthVector(const game::Orientation &orientation) override = 0;

                    Vector3 get3DCoords(const int &x, const int &y) const override = 0;

                    virtual Translation createTranslation(const APlayerModel &player, const int &x, const int &y, const int &timeUnit) override = 0;

                    virtual void translate(const float &deltaUnits, const Vector3 &translationVector, Vector3 &destination, APlayerModel &player) override = 0;

                private:
                    size_t _width;
                    size_t _height;

                    float _tileSize;
            };
        }
    } // namespace gui
} // namespace zappy
