import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.components import sensor, number
from esphome import automation
from esphome.core import coroutine_with_priority
from esphome.const import (
    CONF_ACCURACY_DECIMALS,
    CONF_INPUT,
    CONF_CALIBRATION,
    CONF_ENTITY_CATEGORY,
    CONF_ICON,
    CONF_INITIAL_VALUE,
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_TIMEOUT,
    CONF_WAIT_TIME,
    CONF_RESTORE_VALUE,
    CONF_SET_ACTION,
    CONF_STEP,
    CONF_UNIT_OF_MEASUREMENT,
    ENTITY_CATEGORY_CONFIG,
    ICON_WATER_PERCENT,
    UNIT_HERTZ,
    UNIT_PERCENT,
)

CODEOWNERS = ["@alessiomorale"]

CONF_CALIBRATION_DRY = CONF_CALIBRATION + "_dry"
CONF_CALIBRATION_WET = CONF_CALIBRATION + "_wet"

humidity_sensor_ns = cg.esphome_ns.namespace("humidity_sensor")
HumiditySensor = humidity_sensor_ns.class_("HumiditySensor", sensor.Sensor, cg.Component)

PersistentNumber = humidity_sensor_ns.class_("PersistentNumber", number.Number, cg.Component)

def validate_min_max(config):
    if config[CONF_MAX_VALUE] <= config[CONF_MIN_VALUE]:
        raise cv.Invalid(f"{CONF_MAX_VALUE} must be greater than {CONF_MIN_VALUE}")

    if (config[CONF_INITIAL_VALUE] > config[CONF_MAX_VALUE]) or (
        config[CONF_INITIAL_VALUE] < config[CONF_MIN_VALUE]
    ):
        raise cv.Invalid(
            f"{CONF_INITIAL_VALUE} must be a value between {CONF_MAX_VALUE} and {CONF_MIN_VALUE}"
        )
    return config


    # Optional variables:
    unit_of_measurement: "Hz"





SENSOR_CONFIG_SCHEMA = (
    sensor.sensor_schema(HumiditySensor)
    .extend(
        {
        cv.GenerateID(): cv.declare_id(HumiditySensor),
        cv.Required(CONF_INPUT): cv.use_id(sensor.Sensor),
        cv.Required(CONF_CALIBRATION_DRY): number.NUMBER_SCHEMA.extend(
                {
                    cv.GenerateID(): cv.declare_id(PersistentNumber),
                    cv.Optional(
                        CONF_ENTITY_CATEGORY, default=ENTITY_CATEGORY_CONFIG
                    ): cv.entity_category,
                    cv.Optional(CONF_INITIAL_VALUE, default=15.0): cv.positive_float,
                    cv.Optional(CONF_UNIT_OF_MEASUREMENT, default=UNIT_HERTZ): cv.string,
                    cv.Optional(CONF_MAX_VALUE, default=100): cv.positive_float,
                    cv.Optional(CONF_MIN_VALUE, default=0.1): cv.positive_float,
                    cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                    cv.Optional(CONF_STEP, default=0.1): cv.positive_float,
                    cv.Optional(CONF_ICON, default="mdi:water-plus"): cv.string,
                    cv.Optional(CONF_SET_ACTION): automation.validate_automation(
                        single=True
                    ),
                }
        ),
        cv.Required(CONF_CALIBRATION_WET): number.NUMBER_SCHEMA.extend(
                {
                    cv.GenerateID(): cv.declare_id(PersistentNumber),
                    cv.Optional(
                        CONF_ENTITY_CATEGORY, default=ENTITY_CATEGORY_CONFIG
                    ): cv.entity_category,
                    cv.Optional(CONF_INITIAL_VALUE, default=3.0): cv.positive_float,
                    cv.Optional(CONF_UNIT_OF_MEASUREMENT, default=UNIT_HERTZ): cv.string,
                    cv.Optional(CONF_MAX_VALUE, default=100): cv.positive_float,
                    cv.Optional(CONF_MIN_VALUE, default=0.1): cv.positive_float,
                    cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                    cv.Optional(CONF_STEP, default=0.1): cv.positive_float,
                    cv.Optional(CONF_ICON, default="mdi:water-minus"): cv.string,
                    cv.Optional(CONF_SET_ACTION): automation.validate_automation(
                        single=True
                    ),
                }
        ),
        cv.Optional(CONF_UNIT_OF_MEASUREMENT, default=UNIT_PERCENT): cv.string,
        cv.Optional(CONF_ACCURACY_DECIMALS, default=2): cv.uint8_t,
        cv.Optional(CONF_ICON, default=ICON_WATER_PERCENT): cv.string,
        cv.Optional(CONF_WAIT_TIME, default=500): cv.uint32_t,
        cv.Optional(CONF_TIMEOUT, default=60000): cv.uint32_t,
    }
).extend(cv.COMPONENT_SCHEMA)
)

CONFIG_SCHEMA =  SENSOR_CONFIG_SCHEMA

async def setup_sensor(config, key, setter):
    if key not in config:
        return None
    var = await sensor.new_sensor(config[key])
    cg.add(setter(var))
    return var


async def setup_input(config, key, setter):
    if key not in config:
        return None
    var = await cg.get_variable(config[key])
    cg.add(setter(var))
    return var


# code generation entry point
@coroutine_with_priority(40.0)
async def to_code(config):
    """Code generation entry point"""
    var = await sensor.new_sensor(config)
    await cg.register_component(var, config)

    cal_config = config[CONF_CALIBRATION_DRY]
    numb = await number.new_number(
        cal_config, 
        min_value=cal_config[CONF_MIN_VALUE],
        max_value=cal_config[CONF_MAX_VALUE],
        step=cal_config[CONF_STEP],
    )
    await cg.register_component(
        numb, cal_config
    )

    cg.add(
        numb.set_initial_value(
            cal_config[CONF_INITIAL_VALUE]
        )
    )
    cg.add(
        numb.set_restore_value(
            cal_config[CONF_RESTORE_VALUE]
        )
    )

    cg.add(var.set_calibration_dry(numb))

    cal_config = config[CONF_CALIBRATION_WET]
    numb = await number.new_number(
        cal_config, 
        min_value=cal_config[CONF_MIN_VALUE],
        max_value=cal_config[CONF_MAX_VALUE],
        step=cal_config[CONF_STEP],
    )
    await cg.register_component(
        numb, cal_config
    )

    cg.add(
        numb.set_initial_value(
            cal_config[CONF_INITIAL_VALUE]
        )
    )
    cg.add(
        numb.set_restore_value(
            cal_config[CONF_RESTORE_VALUE]
        )
    )
    cg.add(var.set_calibration_wet(numb))

    # input sensors
    await setup_input(config, CONF_INPUT, var.set_input)

    # exposed sensors
#        await setup_sensor(config, CONF_HUMIDITY, var.set_humidity_output)
    await sensor.register_sensor(var, config)

    # input options
    if CONF_WAIT_TIME in config:
        cg.add(var.set_wait_time(config[CONF_WAIT_TIME]))
    if CONF_TIMEOUT in config:
        cg.add(var.set_timeout(config[CONF_TIMEOUT]))