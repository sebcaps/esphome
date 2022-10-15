import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome import automation
from esphome.automation import maybe_simple_id
from esphome import pins

from esphome.const import (
    CONF_COLOR_TEMPERATURE,
    CONF_GAIN,
    CONF_ID,
    CONF_ILLUMINANCE,
    CONF_GLASS_ATTENUATION_FACTOR,
    CONF_INTEGRATION_TIME,
    CONF_LED_START_ENABLED,
    DEVICE_CLASS_ILLUMINANCE,
    ICON_LIGHTBULB,
    STATE_CLASS_MEASUREMENT,
    UNIT_PERCENT,
    ICON_THERMOMETER,
    UNIT_KELVIN,
    UNIT_LUX,
    CONF_LED_PIN,
)

DEPENDENCIES = ["i2c"]

CONF_RED_CHANNEL = "red_channel"
CONF_GREEN_CHANNEL = "green_channel"
CONF_BLUE_CHANNEL = "blue_channel"
CONF_CLEAR_CHANNEL = "clear_channel"

tcs34725_ns = cg.esphome_ns.namespace("tcs34725")
TCS34725Component = tcs34725_ns.class_(
    "TCS34725Component", cg.PollingComponent, i2c.I2CDevice
)

TCS34725LEDOn = tcs34725_ns.class_("TCS34725LEDOn", automation.Action)
TCS34725LEDOff = tcs34725_ns.class_("TCS34725LEDOff", automation.Action)

TCS34725IntegrationTime = tcs34725_ns.enum("TCS34725IntegrationTime")
TCS34725_INTEGRATION_TIMES = {
    "2.4ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_2_4MS,
    "24ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_24MS,
    "50ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_50MS,
    "101ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_101MS,
    "120ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_120MS,
    "154ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_154MS,
    "180ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_180MS,
    "199ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_199MS,
    "240ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_240MS,
    "300ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_300MS,
    "360ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_360MS,
    "401ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_401MS,
    "420ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_420MS,
    "480ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_480MS,
    "499ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_499MS,
    "540ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_540MS,
    "600ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_600MS,
    "614ms": TCS34725IntegrationTime.TCS34725_INTEGRATION_TIME_614MS,
}

TCS34725Gain = tcs34725_ns.enum("TCS34725Gain")
TCS34725_GAINS = {
    "1X": TCS34725Gain.TCS34725_GAIN_1X,
    "4X": TCS34725Gain.TCS34725_GAIN_4X,
    "16X": TCS34725Gain.TCS34725_GAIN_16X,
    "60X": TCS34725Gain.TCS34725_GAIN_60X,
}

color_channel_schema = sensor.sensor_schema(
    unit_of_measurement=UNIT_PERCENT,
    icon=ICON_LIGHTBULB,
    accuracy_decimals=1,
    state_class=STATE_CLASS_MEASUREMENT,
)
color_temperature_schema = sensor.sensor_schema(
    unit_of_measurement=UNIT_KELVIN,
    icon=ICON_THERMOMETER,
    accuracy_decimals=1,
    state_class=STATE_CLASS_MEASUREMENT,
)
illuminance_schema = sensor.sensor_schema(
    unit_of_measurement=UNIT_LUX,
    accuracy_decimals=1,
    device_class=DEVICE_CLASS_ILLUMINANCE,
    state_class=STATE_CLASS_MEASUREMENT,
)

INTERRUPT_SCHEMA = cv.Schema(
    {
        cv.Optional("interrupt_pin"): cv.All(
            pins.internal_gpio_input_pullup_pin_schema
        ),
        cv.Required("high_level"): cv.All(cv.int_),
        cv.Required("low_level"): cv.All(cv.int_),
    }
)
CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(TCS34725Component),
            cv.Optional(CONF_RED_CHANNEL): color_channel_schema,
            cv.Optional(CONF_GREEN_CHANNEL): color_channel_schema,
            cv.Optional(CONF_BLUE_CHANNEL): color_channel_schema,
            cv.Optional(CONF_CLEAR_CHANNEL): color_channel_schema,
            cv.Optional(CONF_ILLUMINANCE): illuminance_schema,
            cv.Optional(CONF_COLOR_TEMPERATURE): color_temperature_schema,
            cv.Optional(CONF_INTEGRATION_TIME, default="2.4ms"): cv.enum(
                TCS34725_INTEGRATION_TIMES, lower=True
            ),
            cv.Optional(CONF_GAIN, default="1X"): cv.enum(TCS34725_GAINS, upper=True),
            cv.Optional(CONF_GLASS_ATTENUATION_FACTOR, default=1.0): cv.float_range(
                min=1.0
            ),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    .extend(i2c.i2c_device_schema(0x29))
    .extend(
        {
            cv.Optional(CONF_LED_PIN): cv.All(pins.internal_gpio_output_pin_schema),
        }
    )
    .extend(
        {
            cv.Optional(CONF_LED_START_ENABLED, default=True): cv.boolean,
        }
    )
    .extend(INTERRUPT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    cg.add(var.set_integration_time(config[CONF_INTEGRATION_TIME]))
    cg.add(var.set_gain(config[CONF_GAIN]))
    cg.add(var.set_glass_attenuation_factor(config[CONF_GLASS_ATTENUATION_FACTOR]))

    if CONF_RED_CHANNEL in config:
        sens = await sensor.new_sensor(config[CONF_RED_CHANNEL])
        cg.add(var.set_red_sensor(sens))
    if CONF_GREEN_CHANNEL in config:
        sens = await sensor.new_sensor(config[CONF_GREEN_CHANNEL])
        cg.add(var.set_green_sensor(sens))
    if CONF_BLUE_CHANNEL in config:
        sens = await sensor.new_sensor(config[CONF_BLUE_CHANNEL])
        cg.add(var.set_blue_sensor(sens))
    if CONF_CLEAR_CHANNEL in config:
        sens = await sensor.new_sensor(config[CONF_CLEAR_CHANNEL])
        cg.add(var.set_clear_sensor(sens))
    if CONF_ILLUMINANCE in config:
        sens = await sensor.new_sensor(config[CONF_ILLUMINANCE])
        cg.add(var.set_illuminance_sensor(sens))
    if CONF_COLOR_TEMPERATURE in config:
        sens = await sensor.new_sensor(config[CONF_COLOR_TEMPERATURE])
        cg.add(var.set_color_temperature_sensor(sens))
    if CONF_LED_PIN in config:
        pin_led = await cg.gpio_pin_expression(config[CONF_LED_PIN])
        cg.add(var.set_led_pin(pin_led))
    if CONF_LED_START_ENABLED in config:
        cg.add(var.set_led_start_enabled(config[CONF_LED_START_ENABLED]))
    if "interrupt_pin" in config:
        interrupt_pin = await (cg.gpio_pin_expression(config["interrupt_pin"]))
        cg.add(var.set_interrupt_pin(interrupt_pin))
        cg.add(var.set_high_threshold(config["high_level"]))
        cg.add(var.set_low_threshold(config["low_level"]))


LED_ACTION_SCHEMA = maybe_simple_id(
    {cv.Required(CONF_ID): cv.use_id(TCS34725Component)}
)


@automation.register_action("tcs34725.led_on", TCS34725LEDOn, LED_ACTION_SCHEMA)
@automation.register_action("tcs34725.led_off", TCS34725LEDOff, LED_ACTION_SCHEMA)
async def tcs34725_led_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    return cg.new_Pvariable(action_id, template_arg, paren)
