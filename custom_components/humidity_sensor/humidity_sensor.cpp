#include "humidity_sensor.h"
#include "esphome/core/hal.h"
#include "esphome/core/log.h"

#ifndef isnan
using std::isnan;
using std::min;
using std::max;
#endif

namespace esphome {
namespace humidity_sensor {

static const char *const TAG = "humidity_sensor";
static const char *const GAP = "  ";

void HumiditySensor::dump_config() {
  ESP_LOGCONFIG(TAG, "Soil humidity sensors");
  LOG_SENSOR(GAP, "Soil humidity", this->input_);
  LOG_NUMBER(GAP, "Calibration dry", this->calibration_dry_);
  LOG_NUMBER(GAP, "Calibration wet", this->calibration_wet_);
}

void HumiditySensor::setup() {
  if (this->wait_time_) {
    auto cb = [this](float) {
      if (!this->wait_start_) {
        this->wait_start_ = millis();
      }
    };
    this->input_->add_on_state_callback(cb);
  }
  this->publish_state(NAN);
}

void HumiditySensor::loop() {
  if (this->wait_start_ && (millis() - this->wait_start_) > this->wait_time_) {
    this->wait_start_ = 0;
    auto state = this->get_input();
    this->process_input(state);
    this->timeout_start_ = 0;
    return;
  }
  check_timeout();
}

void HumiditySensor::check_timeout(){
  if (!this->timeout_start_)
  {
    this->timeout_start_ = millis();
  }
  if (this->timeout_start_ && (millis() - this->timeout_start_) > this->timeout_) {
    ESP_LOGW(TAG, "[%s] Timeout waiting for sensor input [%s]", this->get_name().c_str(), this->input_->get_name().c_str());

    this->timeout_start_ = 0;
    this->process_input(NAN);
  }
}

// calculates humidity
void HumiditySensor::process_input(float frequency) {

  if(std::isnan(frequency)){
    this->publish_state(NAN);
    return;
  }

  auto calibration_dry = this->get_calibration_dry();
  auto calibration_wet = this->get_calibration_wet();
  if (std::isnan(calibration_dry) || std::isnan(calibration_wet)) {
    return;
  }

  
  auto humidity = this->calc_humidity(frequency, calibration_dry, calibration_wet);
  this->publish_state(humidity);
}

float HumiditySensor::calc_humidity(float frequency, float calibration_dry, float calibration_wet) {
  auto ret = 100.0f - (frequency - calibration_wet) / calibration_dry * 100.0f;

  return max(0.0f, min(ret, 100.0f));
}

}  // namespace humidity_sensor
}  // namespace esphome