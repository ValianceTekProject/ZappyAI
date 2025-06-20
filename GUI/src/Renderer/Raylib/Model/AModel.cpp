/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** AModel.cpp
*/

#include "AModel.hpp"

zappy::gui::raylib::AModel::AModel() :
    _position(Vector3{0, 0, 0}),
    _scale(1),
    _rotation(Vector3{0, 0, 0}),
    _rotationMatrix(MatrixIdentity()),
    _color(WHITE),
    _model()
{}

void zappy::gui::raylib::AModel::init()
{
    _updateTransform();
}

void zappy::gui::raylib::AModel::setRotation(const Vector3 &rotation)
{
    this->_rotation = rotation;
}

void zappy::gui::raylib::AModel::translate(const Vector3 &translation)
{
    this->_position = Vector3Add(_position, translation);
}

void zappy::gui::raylib::AModel::rotate(const Vector3 &rotation)
{
    this->_rotation.x += rotation.x;
    this->_rotation.y += rotation.y;
    this->_rotation.z += rotation.z;

    _updateTransform();
}

void zappy::gui::raylib::AModel::render()
{
    DrawModel(_model, _position, _scale, _color);
}

void zappy::gui::raylib::AModel::_updateTransform()
{
    Vector3 rotationRad = {
        this->_rotation.x * DEG2RAD,
        this->_rotation.y * DEG2RAD,
        this->_rotation.z * DEG2RAD
    };

    Matrix R = MatrixRotateXYZ(rotationRad);

    this->_rotationMatrix = R;
    _model.transform = _rotationMatrix;
}

void zappy::gui::raylib::AModel::_initModel(const std::string &modelPath)
{
    this->_model = LoadModel(modelPath.c_str());
    if (_model.meshCount == 0)
        std::cerr << modelPath.c_str() << "Model not load" << std::endl;
}
