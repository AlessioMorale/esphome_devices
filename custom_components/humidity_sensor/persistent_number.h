#pragma once
#include "esphome/core/application.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"
#include "esphome/components/number/number.h"
#include "esphome/core/automation.h"

namespace esphome {
namespace humidity_sensor {

class PersistentNumber : public number::Number, public Component {
  static constexpr char *const TAG = "Persistent number";
  static constexpr char *const GAP = "  ";

 public:
  void dump_config() override { LOG_NUMBER(GAP, "number", this); }

  float get_setup_priority() const override { return setup_priority::PROCESSOR; }

  Trigger<float> *get_set_trigger() const { return set_trigger_; }
  void set_initial_value(float initial_value) { initial_value_ = initial_value; }
  void set_restore_value(bool restore_value) { this->restore_value_ = restore_value; }

  void setup() override {
    float value;
    if (!this->restore_value_) {
      value = this->initial_value_;
    } else {
      this->pref_ = global_preferences->make_preference<float>(this->get_object_id_hash());
      if (!this->pref_.load(&value)) {
        if (!std::isnan(this->initial_value_)) {
          value = this->initial_value_;
        } else {
          value = this->traits.get_min_value();
        }
      }
    }
    this->publish_state(value);
  }

 protected:
  void control(float value) override {
    this->set_trigger_->trigger(value);

    this->publish_state(value);

    if (this->restore_value_) {
      ESP_LOGI(TAG, "Storing value");
      this->pref_.save(&value);
    }
  }

  float initial_value_{NAN};
  bool restore_value_{true};
  Trigger<float> *set_trigger_ = new Trigger<float>();

  ESPPreferenceObject pref_;
};
}  // namespace humidity_sensor
}  // namespace esphome