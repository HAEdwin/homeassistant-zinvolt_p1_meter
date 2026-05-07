"""Sensor platform for the Zinvolt P1-dongle Pro integration."""

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
    EntityCategory,
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

# No parallel HTTP calls are ever made from entities.
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class ZinvoltSensorEntityDescription(SensorEntityDescription):
    """Describe a Zinvolt P1-dongle Pro sensor."""

    value_key: str

    def __post_init__(self) -> None:
        """Default translation_key to key."""
        if self.translation_key is None:
            object.__setattr__(self, "translation_key", self.key)


# ── Helpers to reduce phase-sensor repetition ───────────────────────────

_PHASES = (("a", "la", True), ("b", "lb", False), ("c", "lc", False))


def _phase_descriptions(
    measurement: str,
    unit: str,
    device_class: SensorDeviceClass,
    *,
    all_disabled: bool = False,
) -> tuple[ZinvoltSensorEntityDescription, ...]:
    """Generate Phase A / B / C sensor descriptions for a measurement."""
    return tuple(
        ZinvoltSensorEntityDescription(
            key=f"phase_{letter}_{measurement}",
            native_unit_of_measurement=unit,
            device_class=device_class,
            state_class=SensorStateClass.MEASUREMENT,
            entity_registry_enabled_default=False if all_disabled else enabled,
            value_key=f"{prefix}_{measurement}",
        )
        for letter, prefix, enabled in _PHASES
    )


_ENERGY_KEYS: tuple[tuple[str, str], ...] = (
    ("positive_total_energy", "Positive_total_electric"),
    ("reverse_total_energy", "Reverse_total_electric"),
    ("off_peak_positive_energy", "Off_peak_Positive_electric"),
    ("flat_section_positive_energy", "Flat_section_Positive_electric"),
    ("off_peak_reverse_energy", "Off_peak_Reverse_electric"),
    ("flat_section_reverse_energy", "Flat_section_Reverse_electric"),
)

SENSOR_DESCRIPTIONS: tuple[ZinvoltSensorEntityDescription, ...] = (
    # ── Device info sensors (diagnostic) ────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="device_type",
        value_key="type",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    ZinvoltSensorEntityDescription(
        key="device_model",
        value_key="model",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    # ── Total power (W) ─────────────────────────────────────────────────
    ZinvoltSensorEntityDescription(
        key="total_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="total_power",
    ),
    # ── Per-phase power / voltage / current ─────────────────────────────
    *_phase_descriptions("power", UnitOfPower.WATT, SensorDeviceClass.POWER),
    *_phase_descriptions(
        "voltage",
        UnitOfElectricPotential.VOLT,
        SensorDeviceClass.VOLTAGE,
        all_disabled=True,
    ),
    *_phase_descriptions(
        "current", UnitOfElectricCurrent.AMPERE, SensorDeviceClass.CURRENT
    ),
    # ── Energy sensors (kWh) – total increasing ─────────────────────────
    *(
        ZinvoltSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            value_key=value_key,
        )
        for key, value_key in _ENERGY_KEYS
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Zinvolt P1-dongle Pro sensor entities."""
    coordinator: ZinvoltP1Coordinator = entry.runtime_data

    async_add_entities(
        ZinvoltP1SensorEntity(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class ZinvoltP1SensorEntity(CoordinatorEntity[ZinvoltP1Coordinator], SensorEntity):
    """Representation of a Zinvolt P1-dongle Pro sensor."""

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
            name=f"Zinvolt P1-dongle Pro ({serial})",
            manufacturer="Zinvolt",
            model="P1-dongle Pro",
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
