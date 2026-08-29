from src.GEELoader import GEELoader
import ee
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    loader = GEELoader.GEELoader(os.getenv("PROJECT_ID"))
    etna_region = ee.Geometry.Rectangle([14.92, 37.70, 15.08, 37.80])
    start_date = "2024-07-04"
    end_date = "2024-07-12"
    max_cloud = 20.0

    scenes = loader.fetch_previews(
        start_date=start_date, 
        end_date=end_date, 
        aoi=etna_region, 
        source=["Sentinel-1", "Sentinel-2"], 
        max_cloud=max_cloud)


    loader.download_scenes(scenes, etna_region)


if __name__ == "__main__":
    main()