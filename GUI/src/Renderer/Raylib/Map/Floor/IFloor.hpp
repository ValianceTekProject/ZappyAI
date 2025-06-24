/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IFloor.hpp
*/

#pragma once

#include "Orientation.hpp"
#include "Map.hpp"
#include "AssetPaths.hpp"
#include "APlayerModel.hpp"

#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {

            struct Translation {
                int id;
                Vector3 destination;
                Vector3 translationVector;
                int timeUnits;
                float elapsedTime;
            };

            class IFloor {
                public:
                    virtual ~IFloor() = default;

                    virtual void init() = 0;
                    virtual void update() const = 0;
                    virtual void render() const = 0;

                    // Setters
                    virtual void setWidth(const size_t &width) = 0;
                    virtual void setHeight(const size_t &height) = 0;
                    virtual void setTileSize(const float &tileSize) = 0;

                    // Getters
                    virtual size_t getWidth() const = 0;
                    virtual size_t getHeight() const = 0;
                    virtual float getTileSize() const = 0;

                    virtual Vector3 getGapFromOrientation(const game::Orientation &orientation) = 0;
                    virtual Vector3 getNorthVector(const game::Orientation &orientation) = 0;

                    virtual Vector3 get3DCoords(const int &x, const int &y) const = 0;

                    virtual Translation createTranslation(const APlayerModel &player, const int &x, const int &y, const int &timeUnit) = 0;

                    virtual void translate(const float &deltaUnits, const Vector3 &translationVector, Vector3 &destination, APlayerModel &player) = 0;
            };
        }
    } // namespace gui
} // namespace zappy
