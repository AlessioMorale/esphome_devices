#pragma once

#include "esphome/core/component.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "persistent_number.h"
namespace esphome {
namespace humidity_sensor {

using sensor::Sensor;

//TODO: add timeout and clamp to 0 when not receiving inputs

class HumiditySensor : public Component, public sensor::Sensor {
 public:
  float get_setup_priority() const override { return esphome::setup_priority::DATA; }

  void dump_config() override;
  void setup() override;
  void loop() override;

  // inputs
  void set_input(Sensor *sensor) { this->input_ = sensor; }
  void set_calibration_dry(PersistentNumber *calibration_dry) { this->calibration_dry_ = calibration_dry; }
  void set_calibration_wet(PersistentNumber *calibration_wet) { this->calibration_wet_ = calibration_wet; }
  void set_wait_time(uint32_t value) { this->wait_time_ = value; }
  void set_timeout(uint32_t value) { this->timeout_ = value; }

 protected:
  // input sensors
  Sensor *input_{nullptr};
  PersistentNumber *calibration_dry_{};
  PersistentNumber *calibration_wet_{};

  float get_input() { return this->input_->get_state(); }
  float get_calibration_dry() { return this->calibration_dry_->state; }
  float get_calibration_wet() { return this->calibration_wet_->state; }

  void check_timeout();
  void process_input(float frequency);
  float calc_humidity(float frequency, float calibration_dry, float calibration_wet);

  uint32_t wait_start_{0};
  uint32_t wait_time_{0};
  uint32_t timeout_{0};
  uint32_t timeout_start_{0};
};

}  // namespace humidity_sensor
}  // namespace esphome