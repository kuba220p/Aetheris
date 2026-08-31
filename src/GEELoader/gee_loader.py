import ee
import geemap
import rasterio
from pathlib import Path
from datetime import datetime, timezone

from .scene_metadata import SceneMetadata

class Loader:
    def __init__(self, project_id: str):
        ee.Initialize(project=project_id)
        self.handlers = {
            "Sentinel-1": self.fetch_sentinel1_previews,
            "Sentinel-2": self.fetch_sentinel2_previews,
        }
        self.thumbnail = {
            "Sentinel-1": {
                "bands": ["VV"],
                "min": -25,
                "max": 0,
                "dimensions": 256,
                "format": "png",
            },
            "Sentinel-2": {
                "bands": ["B4", "B3", "B2"],
                "min": 0,
                "max": 3000,
                "dimensions": 256,
                "format": "png",
            }
        }

        self.bands = {
            "Sentinel-2": ["B2", "B3", "B4", "B8", "B11", "B12"],
            "Sentinel-1": ["VV", "VH"],
        }

    def download_scenes(self, scenes: list[SceneMetadata], aoi: ee.Geometry, output_dir = "data/raw", scale: int = 20) -> None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        for scene in scenes:
            clean_date = scene.timestamp.replace(":", "").replace(" ", "_").replace("-", "")
            orbit_suffix = f"_{scene.orbit_pass}" if scene.sensor == "Sentinel-1" else ""
            filename = out / f"{scene.sensor}_{clean_date}{orbit_suffix}.tif"
            self.download_scene(scene, aoi, str(filename), scale)

    def download_scene(self, scene: SceneMetadata, aoi: ee.Geometry, filename: str, scale: int = 20) -> None:
        bands = self.bands[scene.sensor]
        export_img = scene.ee_image.select(bands)
        print(f"Downloading {filename}")
        geemap.ee_export_image(
            ee_object=export_img,
            filename=filename,
            scale=scale,
            region=aoi,
            file_per_band=False
        )
        self.save_metadata(filename, scene, bands)

    def save_metadata(self, filename: str, scene: SceneMetadata, bands: list[str]) -> None:
        with rasterio.open(filename, "r+") as img:
            img.descriptions = tuple(bands)
            img.update_tags(
                SENSOR=scene.sensor,
                SCENE_ID=scene.scene_id,
                TIMESTAMP=scene.timestamp,
                ORBIT_PASS=scene.orbit_pass,
                CLOUD_COVERAGE=scene.cloud_coverage
            )

    def fetch_previews(self, start_date: str, end_date: str, aoi: ee.Geometry, source: list[str], **kwargs) -> list[SceneMetadata]:
        if not source:
            return []

        results: list[SceneMetadata] = []
        for src in source:
            handler = self.handlers.get(src)
            if not handler:
                raise ValueError(f"Unsupported source: {src}")

            results.extend(handler(aoi, start_date, end_date, **kwargs))

        return results
            

    def fetch_sentinel2_previews(self, aoi: ee.Geometry, start_date: str, end_date: str, max_cloud: float) -> list[SceneMetadata]:
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', max_cloud))
            .sort('system:time_start', True)
            )

        return self._loop_collection(collection, aoi, "Sentinel-2")

    def fetch_sentinel1_previews(self, aoi: ee.Geometry, start_date: str, end_date: str, **kwargs) -> list[SceneMetadata]:
        collection = (
            ee.ImageCollection("COPERNICUS/S1_GRD")
            .filterBounds(aoi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.eq("instrumentMode", "IW"))
            .filter(ee.Filter.listContains("transmitterReceiverPolarisation", "VV"))
            .sort("system:time_start", True)
            )

        return self._loop_collection(collection, aoi, "Sentinel-1")

    def _loop_collection(self, collection: ee.ImageCollection, aoi: ee.Geometry, sensor: str) -> list[SceneMetadata]:
        results = []
        for feature in collection.getInfo().get("features", []):
            fid = feature["id"]
            img = ee.Image(fid).clip(aoi)
            results.append(self._make_scene_metadata(
                scene_id=fid,
                sensor=sensor,
                timestamp=self._timestamp(feature["properties"].get("system:time_start", 0)),
                thumbnail_url=self._thumbnail(img, sensor),
                ee_image=img,
                orbit_pass=feature["properties"].get("orbitProperties_pass", "N/A"),
                cloud_coverage=feature["properties"].get("CLOUDY_PIXEL_PERCENTAGE", 0.0),
            ))
        return results

    def _thumbnail(self, img: ee.Image, sensor: str) -> str:
        return img.getThumbURL(self.thumbnail[sensor])

    def _timestamp(self, ts_ms: int) -> str:
        dt = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _make_scene_metadata(
        self, 
        scene_id: str,
        sensor: str, 
        timestamp: str,  
        thumbnail_url: str, 
        ee_image: ee.Image, 
        cloud_coverage:float, 
        orbit_pass: str) -> SceneMetadata:
    
        return SceneMetadata(
            scene_id=scene_id,
            sensor=sensor,
            timestamp=timestamp,
            cloud_coverage=cloud_coverage,
            orbit_pass=orbit_pass,
            thumbnail_url=thumbnail_url,
            ee_image=ee_image
        )