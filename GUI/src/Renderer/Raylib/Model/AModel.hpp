/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AModel.hpp
*/

#pragma once

#include "AssetPaths.hpp"
#include "RendererError.hpp"

#include <iostream>
#include <raylib.h>
#include <raymath.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AModel {
                public:
                    AModel();
                    virtual ~AModel() = default;

                    virtual void init();

                    // Setters
                    virtual void setPosition(const Vector3 &position) { this->_position = position; }

                    virtual void setScale(const float &scale) { this->_scale = scale; }
                    virtual void setRotation(const Vector3 &rotation);

                    // Getters
                    virtual Vector3 getPosition() const { return this->_position; }

                    virtual float getScale() const { return this->_scale; }
                    virtual Vector3 getRotation() const { return this->_rotation; }

                    virtual void update() = 0;

                    virtual void scale(const float &scale) { this->_scale = scale; }
                    virtual void translate(const Vector3 &translation);
                    virtual void rotate(const Vector3 &rotation);

                    virtual void render();

                protected:
                    virtual void _initModel(const std::string &modelPath);

                    void _updateTransform();

                    Vector3 _position;

                    float _scale;
                    Vector3 _rotation;
                    Matrix  _rotationMatrix;

                    Color _color;

                    Model _model;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
