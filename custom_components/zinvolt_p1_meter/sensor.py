"""Sensor platform for the Zinvolt P1 Meter integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ZinvoltP1Coordinator


@dataclass(frozen=True, kw_only=True)
class ZinvoltSensorEntityDescription(SensorEntityDescription):
    """Describe a Zinvolt P1 Meter sensor."""

    value_key: str


SENSOR_DESCRIPTIONS: tuple[ZinvoltSensorEntityDescription, ...] = (
    # ── Device info sensors (diagnostic) ────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="device_type",
        translation_key="device_type",
        value_key="type",
        entity_registry_enabled_default=False,
    ),
    ZinvoltSensorEntityDescription(
        key="device_model",
        translation_key="device_model",
        value_key="model",
        entity_registry_enabled_default=False,
    ),
    # ── Power sensors (W) ───────────────────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="total_power",
        translation_key="total_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="total_power",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_a_power",
        translation_key="phase_a_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="la_power",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_b_power",
        translation_key="phase_b_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lb_power",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_c_power",
        translation_key="phase_c_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lc_power",
    ),
    # ── Voltage sensors (V) ─────────────────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="phase_a_voltage",
        translation_key="phase_a_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="la_voltage",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_b_voltage",
        translation_key="phase_b_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lb_voltage",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_c_voltage",
        translation_key="phase_c_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lc_voltage",
    ),
    # ── Current sensors (A) ─────────────────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="phase_a_current",
        translation_key="phase_a_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="la_current",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_b_current",
        translation_key="phase_b_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lb_current",
    ),
    ZinvoltSensorEntityDescription(
        key="phase_c_current",
        translation_key="phase_c_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_key="lc_current",
    ),
    # ── Energy sensors (kWh) – total increasing ─────────────────────────
    ZinvoltSensorEntityDescription(
        key="positive_total_energy",
        translation_key="positive_total_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Positive_total_electric",
    ),
    ZinvoltSensorEntityDescription(
        key="reverse_total_energy",
        translation_key="reverse_total_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Reverse_total_electric",
    ),
    ZinvoltSensorEntityDescription(
        key="off_peak_positive_energy",
        translation_key="off_peak_positive_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Off_peak_Positive_electric",
    ),
    ZinvoltSensorEntityDescription(
        key="flat_section_positive_energy",
        translation_key="flat_section_positive_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Flat_section_Positive_electric",
    ),
    ZinvoltSensorEntityDescription(
        key="off_peak_reverse_energy",
        translation_key="off_peak_reverse_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Off_peak_Reverse_electric",
    ),
    ZinvoltSensorEntityDescription(
        key="flat_section_reverse_energy",
        translation_key="flat_section_reverse_energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_key="Flat_section_Reverse_electric",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zinvolt P1 Meter sensor entities."""
    coordinator: ZinvoltP1Coordinator = entry.runtime_data

    async_add_entities(
        ZinvoltP1SensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ZinvoltP1SensorEntity(CoordinatorEntity[ZinvoltP1Coordinator], SensorEntity):
    """Representation of a Zinvolt P1 Meter sensor."""

    entity_description: ZinvoltSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZinvoltP1Coordinator,
        description: ZinvoltSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description

        serial = coordinator.serial_number or "unknown"
        self._attr_unique_id = f"{serial}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=f"Zinvolt P1 Meter ({serial})",
            manufacturer="Zinvolt",
            model="P1 Meter",
            sw_version=(coordinator.data or {}).get("Meter_version"),
            serial_number=serial,
            configuration_url=coordinator.url,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not (data := self.coordinator.data):
            return None
        return data.get(self.entity_description.value_key)
