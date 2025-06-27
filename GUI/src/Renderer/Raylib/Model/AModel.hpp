/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AModel.hpp
*/

#pragma once

#include "IModel.hpp"
#include "AssetPaths.hpp"
#include "RendererError.hpp"

#include <iostream>
#include <raylib.h>
#include <raymath.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class AModel : public IModel {
                public:
                    AModel();
                    virtual ~AModel() = default;

                    virtual void init();

                    // Setters
                    virtual void setPosition(const Vector3 &position) override { this->_position = position; }

                    virtual void setScale(const float &scale) override { this->_scale = scale; }
                    virtual void setRotation(const Vector3 &rotation) override;

                    virtual void setColor(const Color &color) override { this->_color = color; }

                    // Getters
                    virtual Vector3 getPosition() const override { return this->_position; }

                    virtual float getScale() const override { return this->_scale; }
                    virtual Vector3 getRotation() const override { return this->_rotation; }

                    virtual Color getColor() const override { return this->_color; }

                    virtual void update(const float &deltaUnits) override = 0;

                    virtual void scale(const float &scale) override { this->_scale = scale; }
                    virtual void translate(const Vector3 &translation) override;
                    virtual void rotate(const Vector3 &rotation) override;

                    virtual void render() override;

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
