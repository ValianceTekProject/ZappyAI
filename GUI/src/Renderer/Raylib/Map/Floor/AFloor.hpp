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
                    AFloor(size_t width, size_t height, size_t tileSize);
                    ~AFloor() = default;

                    virtual void init() override;
                    virtual void update() const override;
                    virtual void render() const override;

                    // Setters
                    void setWidth(size_t width) override { this->_width = width; }
                    void setHeight(size_t height) override { this->_height = height; }
                    void setTileSize(size_t tileSize) override { this->_tileSize = tileSize; }

                    // Getters
                    size_t getWidth() const override { return _width; }
                    size_t getHeight() const override { return _height; }
                    size_t getTileSize() const override { return _tileSize; }

                private:
                    size_t _width;
                    size_t _height;

                    size_t _tileSize;
            };
        }
    } // namespace gui
} // namespace zappy
