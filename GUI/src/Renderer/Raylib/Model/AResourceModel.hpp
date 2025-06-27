/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** AResourceModel.hpp
*/

#pragma once

#include "AModel.hpp"
#include "Resource.hpp"


namespace zappy {
    namespace gui {
        namespace raylib {
            class AResourceModel : public AModel {
                public:
                    AResourceModel(const int &id, const zappy::game::Resource &resourceType);
                    virtual ~AResourceModel() = default;

                    virtual void init() override;

                    // Setters
                    void setGamePosition(const Vector2 &position) { this->_gamePosition = position; }

                    // Getters
                    int getId() const { return this->_id; }

                    Vector2 getGamePosition() const { return this->_gamePosition; }

                    virtual void update(const float &deltaUnits) override { (void)deltaUnits; }

                protected:
                    virtual void _initModel(const std::string &modelPath) override;

                    int _id;
                    Vector2 _gamePosition;
                    zappy::game::Resource _resourceType;

                    float _scale;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
