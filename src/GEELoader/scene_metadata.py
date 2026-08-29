import ee
from dataclasses import dataclass


@dataclass
class SceneMetadata:
    scene_id: str
    sensor: str
    timestamp: str
    cloud_coverage: float
    orbit_pass: str
    thumbnail_url: str
    ee_image: ee.Image